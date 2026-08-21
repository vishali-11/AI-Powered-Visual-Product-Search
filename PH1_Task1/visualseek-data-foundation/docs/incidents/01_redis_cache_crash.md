# Incident: Redis cache crash under traffic spike

| Field | Detail |
|---|---|
| Severity | High |
| Data source affected | User Interaction / Clickstream caching layer (Redis) |
| Duration | ~3 hours |
| Users affected | ~10,000 |
| Business impact | 15% drop in sales during the incident window |

## Root Cause
An unexpected increase in traffic exceeded the Redis instance's capacity, leading to a crash.

## Impact
Approximately 10,000 users experienced increased search latency, causing a 15% drop in sales over a 3-hour period.

## Detection
Detected via Datadog alerts indicating high latency and error rates on cache lookups.

## Mitigation
Scaled the Redis instance and implemented a Redis Cluster setup to distribute load more effectively.

## Interview-Ready Answer
"During a traffic spike, our Redis cache went down, impacting search performance. I identified the issue through Datadog alerts and quickly scaled our Redis instance, later setting up a Redis Cluster to prevent future occurrences. This experience taught me the importance of monitoring and scalability in system design."
