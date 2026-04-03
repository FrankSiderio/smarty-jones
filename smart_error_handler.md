# Smarty Jones (Smart Error Handler)

A lightweight debugging assistant that (given good context) will identify failures in code and provide specifics on what went wrong & how to fix it.

## Context
In order for Smarty Jones to do a good job, it needs good context. What makes good context?

### Error Exception (including a stack trace)

Smarty needs to know what the error message is and a stack trace of that exception so it has a starting point as to what is wrong

### Input
Whether it is input files or function parameters it helps to know what the exact inputs to the function are

### Source code
The code that is actually executing the functionality allows smarter to learn about how things work to better determine what went wrong to cause the error

### Documentation
Additional information about architecture, data models, code design, etc will help smarty determine what the issue is

---

## Usage
```python
from smarty_jones import SmartyJonesHandler

SmartyJonesHandler.install(endpoint_url="https://your-ai-service.com/analyze", api_token="your API KEY")
```

## Default Prompt

```
You are an expert debugger with the sole goal of providing really useful error messages stating exactly what went wrong and potentially a way to fix it.
- analyze the context and read the stack trace
  - context should include an error message and stack trace
- provide a helpful error message
  - please note that the AI message is generated 
- if you are unable to figure out what the error is then state that, provide what additional information you would need to give a better error message

context:

{{context}}

```

## goals:
- pip library that is really lightweight and easy to implement
- how do we make this secure? don't want to read any secrets or sensitive information
  - think we need to have the prompt on the library side, this way no one can prompt inject
- support for pure LLM or MCP