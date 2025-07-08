# API Reference

## MCP Tools

### pan_inline_scan

Scans a single prompt/response pair for security threats.

**Parameters:**
- `prompt` (string): The user's input message
- `response` (string): The AI's response message

**Returns:**
```json
{
  "success": true,
  "scan_id": "uuid",
  "verdict": "benign|malicious",
  "action": "allow|block",
  "threats": ["prompt:injection", "response:toxic_content"]
}
```

### pan_batch_scan

Scans multiple prompt/response pairs in a single request.

**Parameters:**
- `scan_objects` (array): List of objects with `prompt` and `response` fields (max 5)

**Returns:**
```json
{
  "success": true,
  "scan_ids": ["uuid1", "uuid2"],
  "count": 2
}
```

### pan_get_scan_results

Retrieves results for previously submitted scans.

**Parameters:**
- `scan_ids` (array): List of scan IDs (max 20)

**Returns:**
```json
{
  "success": false,
  "error": "Not yet implemented"
}
```

### pan_get_scan_reports

Gets detailed threat analysis reports.

**Parameters:**
- `scan_ids` (array): List of scan IDs

**Returns:**
```json
{
  "success": false,
  "error": "Not yet implemented"
}
```

## Threat Types

### Prompt-Based Threats
- `injection`: Prompt injection attempts
- `jailbreak`: Attempts to bypass safety measures
- `malicious_code`: Requests for harmful code
- `toxic_content`: Offensive or harmful content

### Response-Based Threats
- `data_exposure`: Potential data leakage
- `ungrounded`: Hallucinated content
- `malicious_urls`: Suspicious links
- `policy_violation`: Custom policy breaches
