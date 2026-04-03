# Smarty Jones - Minimal Version

A super lightweight debugging assistant - HTTP endpoint only.

## Quick Test

```python
from smarty_jones import SmartyJonesHandler

# Connect to your AI service
SmartyJonesHandler.install(
    endpoint_url="https://your-ai-service.com/analyze",
    api_token="your-api-key"
)

# Now trigger an error to test
def test_function():
    return 1 / 0

test_function()  # This will send error to your AI service
```