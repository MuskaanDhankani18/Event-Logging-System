from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from hashlib import sha256
import json

from validator import validator

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client["event_logs_db"]
collection = db["events"]

collection.create_index([("event_type", ASCENDING)])
collection.create_index([("timestamp", DESCENDING)])
collection.create_index([("source_app_id", ASCENDING)])

# In-memory storage for event logs
event_logs_list = []

def calculate_hash(log):
    log_copy = log.copy()

    # Ensure the timestamp is in ISO format
    if "timestamp" in log_copy and isinstance(log_copy["timestamp"], datetime):
        log_copy["timestamp"] = log_copy["timestamp"].isoformat()

    log_str = json.dumps(log_copy, sort_keys=True)
    return sha256(log_str.encode()).hexdigest()

def truncate_to_milliseconds(dt):
    """Truncate a datetime object to millisecond precision."""
    return dt.replace(microsecond=(dt.microsecond // 1000) * 1000)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/events', methods=['POST'])
def receive_event():
    """Endpoint to receive event logs."""
    try:
        event = request.json
        fields = ['event_type', 'timestamp', 'source_app_id', 'data_payload']
        if not all(field in event for field in fields):
            return jsonify({"error": "Missing required fields"}), 400
        event["timestamp"] = datetime.fromisoformat(event["timestamp"])
        event["timestamp"] = truncate_to_milliseconds(event["timestamp"])

        if not validator.validate(event):
            return jsonify({"error": "Validation failed", "details": validator.errors}), 400

        latest_event = collection.find_one(sort=[("timestamp", DESCENDING)])
        prev_hash = latest_event["current_hash"] if latest_event else None

      #  prev_hash = event_logs_list[-1]["current_hash"] if event_logs_list else None
        event["previous_hash"] = prev_hash
        event["current_hash"] = calculate_hash(event)
        # store in a list
       # event_logs_list.append(event)
        # store in the mongoDB
        print("going to insert")
        collection.insert_one(event)
        return jsonify({"message": "Event received successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/events', methods=['GET'])
def get_events():
    """Endpoint to fetch event logs with filtering and pagination."""
    # Fetch query parameters
    event_type = request.args.get('event_type')
    source_app_id = request.args.get('source_app_id')
    start_timestamp = request.args.get('start_timestamp')
    end_timestamp = request.args.get('end_timestamp')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    # Build query
    query = {}
    if event_type:
        query["event_type"] = event_type
    if source_app_id:
        query["source_app_id"] = source_app_id
    if start_timestamp and end_timestamp:
        query["timestamp"] = {
            "$gte": datetime.fromisoformat(start_timestamp),
            "$lte": datetime.fromisoformat(end_timestamp)
        }

    # Pagination
    skip = (page - 1) * page_size
    logs = list(collection.find(query).skip(skip).limit(page_size))
    total_logs = collection.count_documents(query)

    # Convert ObjectId to string for JSON serialization
    for log in logs:
        log["_id"] = str(log["_id"])

    print(logs)

    return jsonify({
        "total_logs": total_logs,
        "page": page,
        "page_size": page_size,
        "logs": logs
    }), 200


@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Fetch all logs for the dashboard."""
    logs = list(collection.find().sort("timestamp", 1))

    # Format timestamp and convert ObjectId to string for JSON serialization
    for log in logs:
        log["_id"] = str(log["_id"])  # Convert ObjectId to string
        log["timestamp"] = log["timestamp"].isoformat()  # Convert datetime to ISO format string

    return jsonify(logs)


@app.route('/api/verify', methods=['GET'])
def verify_chain():
    """Verify the integrity of the event log chain stored in MongoDB."""
    try:
        # Fetch all logs from MongoDB sorted by timestamp (or insertion order)
        logs = list(collection.find().sort("timestamp", ASCENDING))

        if not logs:
            return jsonify({"message": "No logs to verify"}), 200

        # Initialize variables for verification
        is_valid = True
        invalid_entries = []
        previous_hash = None

        for log in logs:
            # Extract the current document fields
            current_hash = log.get("current_hash")
            recalculated_hash = calculate_hash({
                "event_type": log["event_type"],
                "timestamp": log["timestamp"].isoformat(),
                "source_app_id": log["source_app_id"],
                "data_payload": log["data_payload"],
                "previous_hash": previous_hash
            })

            # Check hash integrity
            if current_hash != recalculated_hash:
                is_valid = False
                invalid_entries.append({
                    "_id": str(log["_id"]),
                    "stored_hash": current_hash,
                    "recalculated_hash": recalculated_hash
                })

            # Update the previous_hash for the next log
            previous_hash = current_hash

        if is_valid:
            return jsonify({"message": "Chain is valid"}), 200
        else:
            return jsonify({
                "message": "Chain integrity compromised",
                "invalid_entries": invalid_entries
            }), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
