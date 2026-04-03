"""
Simple test of Smarty Jones minimal implementation - HTTP endpoint only
"""

from smarty_jones import SmartyJonesHandler


def test_errors():
    """Test error handling with mock HTTP endpoint"""
    
    print("Testing Smarty Jones...")
    
    # Note: This would normally point to a real AI service
    # For testing, you'll need to provide a real endpoint
    mock_endpoint = "https://your-ai-service.com/analyze"
    
    try:
        # Install the handler (this will fail without a real endpoint)
        SmartyJonesHandler.install(
            endpoint_url=mock_endpoint,
            api_token="your-api-token"
        )
        
        print("\n1. Testing ZeroDivisionError:")
        try:
            result = 10 / 0
        except:
            pass  # The handler will show analysis if endpoint works
        
    except Exception as e:
        print(f"Setup failed: {e}")
        print("\nTo test with a real endpoint:")
        print("1. Replace mock_endpoint with your actual AI service URL") 
        print("2. Add your API token")
        print("3. Run the test again")
    
    finally:
        try:
            SmartyJonesHandler.uninstall()
            print("\nCleanup complete!")
        except:
            pass


if __name__ == "__main__":
    test_errors()