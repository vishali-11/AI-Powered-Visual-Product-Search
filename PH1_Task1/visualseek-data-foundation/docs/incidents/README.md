# Incident Postmortems

Reliability incidents observed in the systems underlying VisualSeek's data sources (Section 7 of the [inventory report](../data_sources_inventory_report.md)). Each is a self-contained postmortem: root cause, impact, detection, mitigation, and an interview-ready summary.

| # | Incident | Source affected |
|---|---|---|
| 1 | [Redis cache crash under traffic spike](01_redis_cache_crash.md) | Clickstream caching layer |
| 2 | [TensorFlow inference slowdown at peak](02_tensorflow_inference_latency.md) | Visual search inference pipeline |
| 3 | [Kafka consumer lag delaying indexing](03_kafka_consumer_lag.md) | Catalog sync / event bus |
| 4 | [S3 regional outage affecting images](04_s3_regional_outage.md) | Product image storage |
