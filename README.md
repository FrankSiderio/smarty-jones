# Smarty Jones

A super lightweight debugging assistant that provides AI-powered error analysis with minimal setup.

## Features

- **AI-powered analysis**: Uses Claude Sonnet via ChatOpenAI for intelligent error diagnosis
- **Auto source code analysis**: Automatically reads and analyzes source code from stack traces
- **Rich context support**: Pass files, directories, or complex nested data for better debugging
- **Zero configuration**: Just install and one line to activate
- **Security first**: Library-controlled prompts prevent prompt injection attacks

## Installation

```bash
pip install smarty-jones
```

## Quick Start

```python
from smarty_jones import SmartyJonesHandler

# Install with your OpenAI-compatible endpoint
SmartyJonesHandler.install(
    endpoint_url="https://api.anthropic.com/v1/chat/completions",  # or your endpoint
    api_token="your-api-key",
    model="claude-4-6-sonnet"  # Optional, defaults to claude-4-6-sonnet
)

# Now any unhandled exception gets AI analysis
def test_function():
    return 1 / 0

test_function()  # This will trigger AI-powered error analysis
```

## Advanced Usage

### With Additional Context

```python
# Pass additional context for better analysis
SmartyJonesHandler.install(
    endpoint_url="https://api.anthropic.com/v1/chat/completions",
    api_token="your-api-key",
    model="gpt-4",  # Use different model
    config_file="app.json",                    # Single file
    documentation="/path/to/docs/",            # Entire directory
    user_data={"session_id": "abc123"},        # Custom data
    business_rules="rules.yaml"                # Business context
)
```

### Nested File Paths Support

```python
# Complex nested structures with file paths
SmartyJonesHandler.install(
    endpoint_url="https://api.anthropic.com/v1/chat/completions", 
    api_token="your-api-key",
    model="claude-4-6-sonnet",  # Default model
    config={
        "business_rules_path": "rules.yaml", 
        "user_profiles": ["profile1.json", "profile2.json"]
    }
)
```

## What You'll See

```
🤖 Smarty Jones Analysis:
========================================
📝 You're dividing by zero in line 15 of main.py
💡 Add a check: if denominator != 0 before division
🔍 Context: Variable 'denominator' was set to 0 in the loop above
📊 Confidence: 95%
========================================

Traceback (most recent call last):
  File "main.py", line 15, in <module>
    result = numerator / denominator
ZeroDivisionError: division by zero
```

## How It Works

1. **Global Exception Hooking**: Captures all unhandled exceptions automatically
2. **Source Code Analysis**: Reads the actual source code from your stack trace
3. **Context Collection**: Processes files, directories, and nested data structures
4. **AI Analysis**: Sends structured data to Claude Sonnet for intelligent diagnosis
5. **Formatted Output**: Returns clear, actionable debugging advice

## Uninstalling

```python
SmartyJonesHandler.uninstall()  # Removes the exception handler
```

## Development

```bash
# Clone and install in development mode
git clone https://github.com/FrankSiderio/smarty-jones.git
cd smarty-jones
pip install -e .

# Run the test
python test_minimal.py
```

## Security

- **No prompt injection**: User data is passed as structured JSON, not interpolated into prompts
- **Library-controlled prompts**: All AI instructions are hardcoded in the library
- **Local file reading**: Only reads files you explicitly specify
- **Safe by default**: Won't read system files or execute arbitrary code

## Requirements

- Python 3.8+
- langchain-openai
- langchain-core

Total dependencies: Just 2 lightweight packages!

## License

MIT License - see LICENSE file for details.