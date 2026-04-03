"""
Minimal Smarty Jones Handler - Core functionality only
"""

import sys
import traceback
import json
from typing import Dict, Any, Optional
from urllib.request import urlopen, Request


class SmartyJonesHandler:
    """Minimal smart error handler"""
    
    _installed = False
    _original_excepthook = None
    _endpoint_url = None
    _api_token = None
    
    @classmethod
    def install(cls, endpoint_url: str, api_token: Optional[str] = None):
        """Install the error handler"""
        
        if cls._installed:
            print("SmartyJonesHandler already installed")
            return
            
        if not endpoint_url:
            raise ValueError("endpoint_url is required")
            
        # Store configuration
        cls._endpoint_url = endpoint_url
        cls._api_token = api_token
        
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
            print(f"Captured exit with code {code}")

        sys.excepthook = smart_excepthook
        sys.exit = smart_exit
        cls._installed = True
        print("✅ SmartyJonesHandler installed. YAY! 🎉")
    
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
        
        # Get analysis from HTTP endpoint
        try:
            analysis = cls._call_endpoint(context)
            cls._display_analysis(analysis)
            
        except Exception as e:
            print(f"Analysis failed: {e}")
    
    @classmethod
    def _call_endpoint(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call HTTP endpoint for analysis"""
        print("📡 Calling Smarty Jones endpoint for analysis...")
        payload = {
            "system_prompt": cls._get_system_prompt(),
            "context": context
        }
        
        headers = {"Content-Type": "application/json"}
        if cls._api_token:
            headers["Authorization"] = f"Bearer {cls._api_token}"
            
        data = json.dumps(payload).encode('utf-8')
        request = Request(cls._endpoint_url, data=data, headers=headers, method='POST')
        
        with urlopen(request, timeout=10) as response:
            if response.getcode() == 200:
                result = json.loads(response.read().decode('utf-8'))
                return result
            else:
                raise Exception(f"HTTP {response.getcode()}")
    
    @classmethod
    def _get_system_prompt(cls) -> str:
        """Get the system prompt - controlled by library"""
        return """You are an expert debugger. Analyze the error context and return JSON with:
{
    "error_analysis": "Brief explanation of what went wrong",
    "suggested_fix": "How to fix it", 
    "confidence": 0.8
}

Context will include error_type, error_message, and stack_trace."""
    
    @classmethod
    def _display_analysis(cls, analysis: Dict[str, Any]):
        """Display the analysis results"""
        print("\n🤖 Smarty Jones Analysis:")
        print("=" * 40)
        
        if "error_analysis" in analysis:
            print(f"📝 {analysis['error_analysis']}")
        if "suggested_fix" in analysis:
            print(f"💡 {analysis['suggested_fix']}")
        if "confidence" in analysis:
            conf = analysis["confidence"]
            print(f"📊 Confidence: {conf:.0%}" if isinstance(conf, (int, float)) else f"📊 Confidence: {conf}")
            
        print("=" * 40 + "\n")