# Incident: TensorFlow model inference slowdown at peak hours

| Field | Detail |
|---|---|
| Severity | Medium-High |
| Data source affected | Product Images → visual search inference pipeline |
| Duration | Peak-hour windows (recurring until fix) |
| Users affected | Users searching during peak hours |
| Business impact | 10% increase in user abandonment during peak hours |

## Root Cause
The deployed model was not optimized for real-time inference, causing increased latency under heavy load.

## Impact
Search response times increased significantly, resulting in a 10% increase in user abandonment rates during peak hours.

## Detection
User reports and performance monitoring tools highlighted the latency issues.

## Mitigation
Applied model optimization techniques, including quantization, and deployed via TensorFlow Serving to enhance inference speed.

## Interview-Ready Answer
"Our TensorFlow model experienced high latency during peak times. I tackled this by optimizing the model for real-time inference using quantization and deploying it with TensorFlow Serving, which improved our response times and reduced user abandonment."
