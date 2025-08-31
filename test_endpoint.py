#!/usr/bin/env python3
"""
Test script to verify the endpoint response structure
"""

from app.core.response import create_success_response_list
from app.services.tools.manager import ToolManager
import json

def test_endpoint_response():
    """Test the endpoint response structure"""
    print("=== Testing Endpoint Response Structure ===\n")
    
    # Simulate what the endpoint does
    manager = ToolManager()
    tools = manager.get_available_tools()
    
    print("1. Raw tools from ToolManager:")
    print(json.dumps(tools[0], indent=2))
    
    print("\n" + "="*50)
    
    # Simulate the endpoint response
    response = create_success_response_list("tools", tools)
    
    print("2. Endpoint response:")
    print(json.dumps(response.body, indent=2))
    
    print("\n" + "="*50)
    print("3. Check for double attributes:")
    
    # Check if there are double attributes
    response_data = json.loads(response.body)
    first_tool = response_data["data"][0]
    
    if "attributes" in first_tool:
        if "attributes" in first_tool["attributes"]:
            print("❌ DOUBLE ATTRIBUTES DETECTED!")
            print("   - First level: attributes")
            print("   - Second level: attributes.attributes")
        else:
            print("✅ No double attributes - structure is correct!")
            print("   - First level: attributes")
            print("   - Contains: name, cmd, variants, etc.")

if __name__ == "__main__":
    test_endpoint_response()
