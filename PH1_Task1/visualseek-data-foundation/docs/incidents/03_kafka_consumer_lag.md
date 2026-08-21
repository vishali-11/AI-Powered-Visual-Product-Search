# Incident: Kafka message lag delaying product indexing

| Field | Detail |
|---|---|
| Severity | Medium |
| Data source affected | Product Catalog sync / clickstream event bus (Kafka) |
| Duration | 2 hours |
| Queries affected | ~20% of search queries |
| Business impact | Outdated search results, likely reducing conversions |

## Root Cause
A misconfiguration in the Kafka consumer group settings led to processing delays.

## Impact
Product search results were outdated for two hours, affecting 20% of search queries and potentially reducing conversions.

## Detection
Detected through monitoring dashboards showing increased message lag in Kafka.

## Mitigation
Adjusted the consumer group settings and increased the number of replicas for the Kafka topic to handle the load better.

## Interview-Ready Answer
"We faced delayed updates in product indexing due to Kafka message lag. After identifying the configuration issue, I optimized the consumer settings and scaled our Kafka setup, reducing message lag and ensuring timely data processing."
