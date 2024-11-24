Req 2C:
Each log should reference the hash of the previous log.

this is not clear, should we maintain the chain of events/logs of an application or regardless of the application? 
In case of horizontal scalling and as the expectation is to have multiple servers (cluster) serving the application, 
the one way i can think of maintaining the order is to depend on the incoming event's timestamp. So for this example i am presuming:
1) the data input for timestamp is always correct
2) the chain of events to be maintained for all events.

Given Tasks's status:

1. Event Logging API: [done]
2. Tamper-Proof Design:[done]
3. Search and Query:[done]
4. Scalability: [partial]
Use MongoDB’s sharding and indexing features to handle a high volume of event logs. [indexing done but no sharding, not enough time]
Demonstrate horizontal scalability of the API. [no demonstration- did not have enough time]
5. Error Handling and Validation :[done]
6. Optional Challenges (Bonus): [not done- not enough time]
7. Decentralization Simulation: [Not done, it requires setting up UI, docker, cluster of servers and a web server to work as reverse proxy and load balancer]
8. Create a lightweight dashboard to visualize the chain of event logs and any inconsistencies. [partial, not enough time]