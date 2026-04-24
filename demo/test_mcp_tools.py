#!/usr/bin/env python3
"""
Test script to demo TodoApp MCP tools
Run: python test_mcp_tools.py
"""

from mcp_server import (
    check_todo_app_status,
    create_todo,
    get_all_todos,
    get_todo_by_id,
    update_todo,
    mark_todo_complete,
    delete_todo,
    get_users,
    add,
    get_chuck_norris_joke
)

def main():
    print("Testing TodoApp MCP Tools")
    print("=" * 50)
    
    # Test 1: Check TodoApp status
    print("\n[1] Checking TodoApp status...")
    status = check_todo_app_status()
    print(status)
    
    # Test 2: Test basic math tool
    print("\n[2] Testing math tool...")
    result = add(25, 17)
    print(f"25 + 17 = {result}")
    
    # Test 3: Get Chuck Norris joke
    print("\n[3] Getting Chuck Norris joke...")
    joke = get_chuck_norris_joke()
    print(f"Joke: {joke}")
    
    # Test 4: Try to get todos (will fail if server not running)
    print("\n[4] Trying to get todos...")
    todos = get_all_todos()
    print(todos)
    
    # Test 5: Try to create a todo (will fail if server not running)
    print("\n[5] Trying to create a todo...")
    create_result = create_todo(
        title="Test MCP Integration",
        description="Created via MCP tool",
        priority=4
    )
    print(create_result)
    
    # Test 6: Try to get users
    print("\n[6] Trying to get users...")
    users = get_users()
    print(users)
    
    print("\n" + "=" * 50)
    print("MCP Tools test completed!")
    print("To test with real data, start TodoApp server first:")
    print("   uvicorn main:app --reload")

if __name__ == "__main__":
    main()
