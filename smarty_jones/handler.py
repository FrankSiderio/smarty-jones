"""
Minimal Smarty Jones Handler - Core functionality only
"""

import sys
import traceback
import json
import os
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class SmartyJonesHandler:
    """Minimal smart error handler"""
    
    _installed = False
    _original_excepthook = None
    _endpoint_url = None
    _api_token = None
    _model = None
    _additional_context = None
    
    @classmethod
    def install(cls, endpoint_url: str, api_token: Optional[str] = None, model: str = "claude-4-6-sonnet", **additional_context):
        """Install the error handler
        
        Args:
            endpoint_url: AI service endpoint
            api_token: API token for authentication
            model: AI model to use (defaults to claude-4-6-sonnet)
            **additional_context: Additional context to send with every error analysis
                Examples:
                - input_params: Function parameters or input data
                - documentation: Architecture notes, data models, etc.
                - project_info: Project description, patterns, conventions
                - environment: Deployment environment, versions, etc.
        """
        
        if cls._installed:
            print("SmartyJonesHandler already installed")
            return
            
        if not endpoint_url:
            raise ValueError("endpoint_url is required")
            
        # Store configuration
        cls._endpoint_url = endpoint_url
        cls._api_token = api_token
        cls._model = model
        cls._additional_context = cls._process_additional_context(additional_context) if additional_context else {}
        
        # Save original exception hook
        cls._original_excepthook = sys.excepthook
        
        # Install our hook
        def smart_excepthook(exc_type, exc_value, exc_traceback):
            try:
                cls._handle_exception(exc_type, exc_value, exc_traceback)
            except Exception as e:
                print(f"Smarty Jones analysis failed: {e}")
            finally:
                # Always call original
                cls._original_excepthook(exc_type, exc_value, exc_traceback)
        
        def smart_exit(code=0, *args, **kwargs):
            print(f"Captured exit with code {code}. Not implemented analysis for exits yet.")

        sys.excepthook = smart_excepthook
        sys.exit = smart_exit
        cls._installed = True
    
    @classmethod
    def _process_additional_context(cls, additional_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process additional context, reading file contents if paths are provided"""
        processed_context = {}
        
        for key, value in additional_context.items():
            processed_context[key] = cls._process_value_for_file_paths(value)
                
        return processed_context
    
    @classmethod
    def _process_value_for_file_paths(cls, value: Any) -> Any:
        """Recursively process a value to find and read file paths"""
        if isinstance(value, str) and cls._is_file_path(value):
            try:
                with open(value, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                return {
                    "file_path": value,
                    "content": cls._filter_sensitive_content(file_content)
                }
            except Exception as e:
                return {
                    "file_path": value,
                    "error": f"Could not read file: {str(e)}"
                }
        elif isinstance(value, str) and cls._is_directory_path(value):
            return cls._process_directory(value)
        elif isinstance(value, dict):
            # Recursively process dictionary values
            processed_dict = {}
            for k, v in value.items():
                processed_dict[k] = cls._process_value_for_file_paths(v)
            return processed_dict
        elif isinstance(value, (list, tuple)):
            # Recursively process list/tuple items
            processed_list = [cls._process_value_for_file_paths(item) for item in value]
            return processed_list if isinstance(value, list) else tuple(processed_list)
        else:
            # Return value as-is for non-string, non-dict, non-list types
            return value
    
    @classmethod
    def _is_file_path(cls, value: str) -> bool:
        """Check if a string value appears to be a file path"""
        if not value or len(value) < 2:
            return False
            
        # Check if it's an existing file
        if os.path.isfile(value):
            return True
            
        # Check if it looks like a file path (has extension and path separators)
        return (
            ('/' in value or '\\' in value or value.startswith('.')) and
            '.' in os.path.basename(value) and
            not value.startswith('http') and
            not '://' in value
        )
    
    @classmethod
    def _is_directory_path(cls, value: str) -> bool:
        """Check if a string value appears to be a directory path"""
        if not value or len(value) < 2:
            return False
            
        # Check if it's an existing directory
        return os.path.isdir(value)
    
    @classmethod
    def _process_directory(cls, directory_path: str, max_files: int = 20, max_file_size: int = 50000) -> Dict[str, Any]:
        """Process a directory by reading all text files within it"""
        try:
            files_content = {}
            files_processed = 0
            
            # Get all files in directory (not subdirectories)
            for filename in os.listdir(directory_path):
                if files_processed >= max_files:
                    files_content["_truncated"] = f"Only showing first {max_files} files"
                    break
                    
                file_path = os.path.join(directory_path, filename)
                
                # Only process regular files, skip directories
                if not os.path.isfile(file_path):
                    continue
                    
                # Skip binary files based on extension
                if cls._is_likely_text_file(filename):
                    try:
                        # Check file size
                        if os.path.getsize(file_path) > max_file_size:
                            files_content[filename] = {
                                "error": f"File too large (>{max_file_size} bytes)"
                            }
                            continue
                            
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        files_content[filename] = {
                            "file_path": file_path,
                            "content": cls._filter_sensitive_content(content)
                        }
                        files_processed += 1
                    except Exception as e:
                        files_content[filename] = {
                            "error": f"Could not read file: {str(e)}"
                        }
                        
            return {
                "directory_path": directory_path,
                "files": files_content,
                "total_files_processed": files_processed
            }
            
        except Exception as e:
            return {
                "directory_path": directory_path,
                "error": f"Could not read directory: {str(e)}"
            }
    
    @classmethod
    def _is_likely_text_file(cls, filename: str) -> bool:
        """Check if a file is likely a text file based on extension"""
        text_extensions = {
            '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
            '.csv', '.log', '.cfg', '.conf', '.ini', '.sh', '.bat', '.sql', '.php', '.rb', '.go',
            '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.rs', '.kt', '.swift', '.r', '.m',
            '.dockerfile', '.gitignore', '.properties', '.toml'
        }
        
        # Exclude potentially sensitive file extensions
        sensitive_extensions = {'.env', '.key', '.pem', '.p12', '.pfx', '.keystore', '.secrets'}
        
        # Get file extension
        _, ext = os.path.splitext(filename.lower())
        
        # Block sensitive files
        if ext in sensitive_extensions:
            return False
        
        # Include files with known text extensions or no extension (like README, Dockerfile)
        return ext in text_extensions or ext == '' or filename.lower() in {
            'readme', 'license', 'changelog', 'dockerfile', 'makefile', 'requirements'
        }
    
    @classmethod
    def _filter_sensitive_content(cls, content: str) -> str:
        """Remove potential secrets from file content"""
        import re
        
        # Common secret patterns to redact
        secret_patterns = [
            # Key-value patterns
            (r'(password\s*[=:]\s*)["\'][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(api_key\s*[=:]\s*)["\'][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(secret\s*[=:]\s*)["\'][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(token\s*[=:]\s*)["\'][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(access_token\s*[=:]\s*)["\'][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(private_key\s*[=:]\s*)["\'][^"\']+["\']', r'\1"[REDACTED]"'),
            
            # Database connection strings
            (r'(mongodb://[^:]+:)[^@]+(@)', r'\1[REDACTED]\2'),
            (r'(postgres://[^:]+:)[^@]+(@)', r'\1[REDACTED]\2'),
            (r'(mysql://[^:]+:)[^@]+(@)', r'\1[REDACTED]\2'),
            
            # Common credential formats
            (r'sk-[a-zA-Z0-9]{32,}', '[REDACTED_API_KEY]'),  # OpenAI-style keys
            (r'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'),  # GitHub tokens
            (r'xoxb-[a-zA-Z0-9-]+', '[REDACTED_SLACK_TOKEN]'),  # Slack tokens
        ]
        
        filtered_content = content
        for pattern, replacement in secret_patterns:
            filtered_content = re.sub(pattern, replacement, filtered_content, flags=re.IGNORECASE)
        
        return filtered_content

    @classmethod
    def uninstall(cls):
        """Remove the error handler"""
        if cls._installed and cls._original_excepthook:
            sys.excepthook = cls._original_excepthook
            cls._installed = False
            print("❌ SmartyJonesHandler uninstalled")
    
    @classmethod
    def _handle_exception(cls, exc_type, exc_value, exc_traceback):
        """Handle an exception"""
        
        # Collect basic context
        context = {
            "error_type": exc_type.__name__,
            "error_message": str(exc_value),
            "stack_trace": ''.join(traceback.format_tb(exc_traceback))
        }
        
        # Extract and examine source code from stack trace
        source_code_info = cls._extract_source_code_from_traceback(exc_traceback)
        if source_code_info:
            context["source_code"] = source_code_info
        
        # Add additional context if provided
        if cls._additional_context:
            context["additional_context"] = cls._additional_context
        
        # Get analysis from ChatOpenAI
        try:
            analysis = cls._call_endpoint(context)
            cls._display_analysis(analysis)
            
        except Exception as e:
            print(f"Analysis failed: {e}")
    
    @classmethod
    def _extract_source_code_from_traceback(cls, exc_traceback) -> List[Dict[str, Any]]:
        """Extract source code from files in the stack trace"""
        source_files = []
        tb = exc_traceback
        
        while tb is not None:
            filename = tb.tb_frame.f_code.co_filename
            line_number = tb.tb_lineno
            function_name = tb.tb_frame.f_code.co_name
            
            # Skip system/library files
            if cls._should_examine_file(filename):
                source_info = cls._read_source_code_around_line(filename, line_number, function_name)
                if source_info:
                    source_files.append(source_info)
            
            tb = tb.tb_next
        
        return source_files
    
    @classmethod
    def _should_examine_file(cls, filename: str) -> bool:
        """Determine if we should examine the source code of this file"""
        # Skip system libraries and site-packages
        skip_patterns = [
            '/lib/python',
            '/site-packages/',
            '/dist-packages/',
            '<frozen',
            '<built-in'
        ]
        
        for pattern in skip_patterns:
            if pattern in filename:
                return False
                
        # Only examine files that exist and are readable
        return os.path.isfile(filename)
    
    @classmethod
    def _read_source_code_around_line(cls, filename: str, line_number: int, function_name: str, context_lines: int = 5) -> Dict[str, Any]:
        """Read source code around a specific line"""
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            start_line = max(1, line_number - context_lines)
            end_line = min(len(lines), line_number + context_lines)
            
            code_lines = []
            for i in range(start_line - 1, end_line):  # -1 for 0-based indexing
                line_num = i + 1
                line_content = lines[i].rstrip()
                is_error_line = (line_num == line_number)
                
                code_lines.append({
                    "line_number": line_num,
                    "content": line_content,
                    "is_error_line": is_error_line
                })
            
            return {
                "filename": os.path.basename(filename),
                "full_path": filename,
                "function_name": function_name,
                "error_line_number": line_number,
                "code_lines": code_lines,
                "total_lines_in_file": len(lines)
            }
            
        except Exception as e:
            return {
                "filename": os.path.basename(filename),
                "full_path": filename,
                "function_name": function_name,
                "error_line_number": line_number,
                "error": f"Could not read source: {str(e)}"
            }

    @classmethod
    def _call_endpoint(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call ChatOpenAI for analysis"""        
        print("📡 Captured error! Calling AI for smart analysis...")
        
        # Initialize ChatOpenAI
        llm = ChatOpenAI(
            model=cls._model,
            base_url=cls._endpoint_url,
            api_key=cls._api_token,
            streaming=False
        )
        
        # Prepare messages
        system_prompt = cls._get_system_prompt()
        context_str = json.dumps(context, indent=2)
        # print(f"🔍 Context sent to AI:\n{context_str}")
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context: {context_str}")
        ]
        
        # Call the LLM
        response = llm.invoke(messages)
        
        # Parse response - expect JSON format
        try:
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # If not valid JSON, create a structured response
            return {
                "error_analysis": response.content,
                "suggested_fix": "Review the error details above",
                "confidence": 0.7
            }
    
    @classmethod
    def _get_system_prompt(cls) -> str:
        """Get the system prompt - controlled by library"""
        return """You are an expert debugger with the sole goal of providing really useful error messages stating exactly what went wrong and potentially a way to fix it.
- analyze the context and read the stack trace
  - context should include an error message and stack trace
- provide a helpful error message
  - please note that the AI message is generated and may not be 100% accurate (give a confidence score if possible)
- if you are unable to figure out what the error is then state that, provide what additional information you would need to give a better error message
"""
    
    @classmethod
    def _display_analysis(cls, analysis: Dict[str, Any]):
        """Display the analysis results"""
        print("\n🤖 Smarty Jones Analysis:")
        print("=" * 40)
        
        if "error_analysis" in analysis:
            print(f"📝 {analysis['error_analysis']}")
        if "suggested_fix" in analysis:
            print(f"💡 {analysis['suggested_fix']}")

        print("=" * 40 + "\n")
    
    @classmethod
    def _filter_sensitive_content(cls, content: str) -> str:
        """Remove potential secrets from file content"""
        import re
        
        # Common secret patterns to redact
        secret_patterns = [
            # Key-value patterns
            (r'(password\s*[=:]\s*)["\'"][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(api_key\s*[=:]\s*)["\'"][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(secret\s*[=:]\s*)["\'"][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(token\s*[=:]\s*)["\'"][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(access_token\s*[=:]\s*)["\'"][^"\']+["\']', r'\1"[REDACTED]"'),
            (r'(private_key\s*[=:]\s*)["\'"][^"\']+["\']', r'\1"[REDACTED]"'),
            
            # Database connection strings
            (r'(mongodb://[^:]+:)[^@]+(@)', r'\1[REDACTED]\2'),
            (r'(postgres://[^:]+:)[^@]+(@)', r'\1[REDACTED]\2'),
            (r'(mysql://[^:]+:)[^@]+(@)', r'\1[REDACTED]\2'),
            
            # Common credential formats
            (r'sk-[a-zA-Z0-9]{32,}', '[REDACTED_API_KEY]'),  # OpenAI-style keys
            (r'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'),  # GitHub tokens
            (r'xoxb-[a-zA-Z0-9-]+', '[REDACTED_SLACK_TOKEN]'),  # Slack tokens
        ]
        
        filtered_content = content
        for pattern, replacement in secret_patterns:
            filtered_content = re.sub(pattern, replacement, filtered_content, flags=re.IGNORECASE)
        
        return filtered_content