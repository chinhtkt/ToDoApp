#!/usr/bin/env python3
"""
Demo script to login and display todos from TodoApp
"""

from mcp_server import (
    todo_login,
    todo_check_auth,
    get_all_todos,
    create_todo,
    get_todo_by_id,
    update_todo,
    mark_todo_complete,
    delete_todo,
    _auth_token
)

def main():
    print("TodoApp Demo - Login and display todos")
    print("=" * 60)
    
    # Step 1: Login
    print("\n[1] Login...")
    login_result = todo_login('demo_user', 'demo123')
    print(login_result)
    
    # Step 2: Check auth status
    print("\n[2] Check auth status...")
    auth_status = todo_check_auth()
    print(auth_status)
    print(f"Token: {_auth_token[:20]}..." if _auth_token else "No token")
    
    # Step 3: Get all todos
    print("\n[3] Display all todos...")
    todos_result = get_all_todos()
    print(todos_result)
    
    # Step 4: Create a demo todo if no todos exist
    if "No todos found" in todos_result:
        print("\n[4] Create demo todo...")
        create_result = create_todo(
            title="Learn FastAPI with MCP",
            description="Integrate MCP server with TodoApp API",
            priority=4,
            complete=False
        )
        print(create_result)
        
        # Get todos again
        print("\n[5] Display todos after creating new...")
        todos_result = get_all_todos()
        print(todos_result)
    
    # Step 5: Demo operations if todos exist
    if "Todo List" in todos_result:
        print("\n6️⃣ Demo additional operations...")
        
        # Create another todo
        create_result = create_todo(
            title="Test MCP Integration",
            description="Check MCP tools functionality",
            priority=2,
            complete=False
        )
        print(f"Create new todo: {create_result}")
        
        # Get all todos again
        print("\n📋 Current todo list:")
        final_todos = get_all_todos()
        print(final_todos)
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")

if __name__ == "__main__":
    main()
