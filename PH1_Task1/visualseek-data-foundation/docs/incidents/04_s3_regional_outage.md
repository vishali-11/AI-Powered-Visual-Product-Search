# Incident: AWS S3 temporary access issues affecting image retrieval

| Field | Detail |
|---|---|
| Severity | Medium |
| Data source affected | Product Images (S3-compatible media store) |
| Duration | 1 hour |
| Users affected | ~5,000 |
| Business impact | 25% decrease in engagement over the incident window |

## Root Cause
A regional outage in AWS affected our S3 bucket accessibility.

## Impact
Approximately 5,000 users were unable to view product images, leading to a 25% decrease in engagement over a one-hour period.

## Detection
AWS status notifications and user feedback alerted us to the problem.

## Mitigation
Implemented a multi-region S3 strategy to ensure redundancy and minimize future disruptions.

## Interview-Ready Answer
"A regional AWS outage temporarily broke image retrieval for our product catalog. Once AWS status notifications and user feedback confirmed the scope, I moved us to a multi-region S3 strategy so a single-region outage wouldn't take down image delivery again."
