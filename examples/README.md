# ARES Examples

This directory contains example scripts and sample data for using ARES.

## Files

### `sample_query.py`
Python script demonstrating how to use the ARES API programmatically.

**Usage:**
```bash
python examples/sample_query.py
```

**Features:**
- System statistics retrieval
- PII detection example
- Document upload
- Document querying

### `example_document.txt`
Sample German document with various PII entities for testing.

**Contains:**
- Names
- Email addresses
- Phone numbers
- Physical addresses
- IBAN codes

## API Usage Examples

### Python (httpx)

```python
import httpx

# Query documents
response = httpx.post(
    "http://localhost:8000/api/v1/query",
    json={"query": "What is the main topic?", "mask_pii": True}
)
result = response.json()
print(result["answer"])
```

### cURL

```bash
# Query
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "mask_pii": true}'

# Upload
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@document.pdf"

# Detect PII
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact Max Mustermann at max@example.com"}'
```

### JavaScript (fetch)

```javascript
// Query documents
const response = await fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is the main topic?',
    mask_pii: true
  })
});
const result = await response.json();
console.log(result.answer);
```

## Testing PII Detection

Use the example document to test PII detection:

```python
from examples.sample_query import detect_pii

with open('examples/example_document.txt', 'r') as f:
    text = f.read()

result = detect_pii(text)
print(f"Detected {result['total_pii']} PII entities")
print(result['entity_breakdown'])
```

## Next Steps

- Modify `sample_query.py` for your use case
- Upload your own documents
- Integrate ARES API into your applications
- Review the main [README.md](../README.md) for full documentation
