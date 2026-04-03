# Quick Start Guide

## Install and Test

```bash
# Navigate to the project
cd /Users/fsider103@cable.comcast.com/Projects/smarty_jones

# Install in development mode
pip install -e .

# Update test_minimal.py with your real endpoint URL and API token
# Then run:
python test_minimal.py
```

## What You'll See

```
Testing Smarty Jones...
✅ SmartyJonesHandler installed

1. Testing ZeroDivisionError:

🤖 Smarty Jones Analysis:
========================================
📝 You're dividing by zero!
💡 Check if denominator is not zero before dividing
📊 Confidence: 90%
========================================

Traceback (most recent call last):
  File "test_minimal.py", line 35, in <module>
    result = 10 / 0
ZeroDivisionError: division by zero

2. Testing KeyError:
...

❌ SmartyJonesHandler uninstalled
Test complete!
```

## Key Files

- `smarty_jones/__init__.py` - Main exports (7 lines)
- `smarty_jones/handler.py` - Core functionality (~150 lines)  
- `test_minimal.py` - Simple test script

**Total: ~160 lines of code, zero dependencies!**