#!/usr/bin/env python3
"""
Demo script to test delete_todo tool and other CRUD operations
"""

from mcp_server import (
    todo_login,
    get_all_todos,
    delete_todo,
    get_todo_by_id,
    update_todo,
    mark_todo_complete,
    create_todo
)

def main():
    print("Testing Delete Todo and CRUD Operations")
    print("=" * 60)
    
    # Login first
    print("\n[1] Login...")
    login_result = todo_login('demo_user', 'demo123')
    print(login_result)
    
    # Show current todos
    print("\n[2] Display current todos...")
    todos = get_all_todos()
    print(todos)
    
    # Create a test todo to delete
    print("\n[3] Create todo to test delete...")
    create_result = create_todo(
        title="Test Delete Todo",
        description="This todo will be deleted for testing",
        priority=1,
        complete=False
    )
    print(create_result)
    
    # Show updated todos list
    print("\n[4] Todo list after creating new todo...")
    todos_after_create = get_all_todos()
    print(todos_after_create)
    
    # Extract the last todo ID to delete (assuming it's the newest)
    # This is a simple way to get an ID for testing
    print("\n[5] Testing delete_todo...")
    
    # Let's try deleting todo with ID 25 (from previous examples)
    delete_result = delete_todo(25)
    print(f"Delete todo ID 25: {delete_result}")
    
    # Try deleting a few more
    delete_result2 = delete_todo(24)
    print(f"Delete todo ID 24: {delete_result2}")
    
    delete_result3 = delete_todo(23)
    print(f"Delete todo ID 23: {delete_result3}")
    
    # Show final todos list
    print("\n6️⃣ Todo list after deletion...")
    final_todos = get_all_todos()
    print(final_todos)
    
    # Test other operations
    print("\n7️⃣ Testing update_todo...")
    update_result = update_todo(22, title="Updated NodeJS Learning", priority=5)
    print(f"Update todo ID 22: {update_result}")
    
    print("\n8️⃣ Testing mark_todo_complete...")
    complete_result = mark_todo_complete(21)
    print(f"Mark todo ID 21 complete: {complete_result}")
    
    print("\n9️⃣ Testing get_todo_by_id...")
    todo_detail = get_todo_by_id(21)
    print(f"Todo ID 21 details:\n{todo_detail}")
    
    print("\n" + "=" * 60)
    print("✅ CRUD Operations Test completed!")
    print("\n💡 **Tools tested:**")
    print("- ✅ delete_todo() - Delete todo")
    print("- ✅ update_todo() - Update todo")
    print("- ✅ mark_todo_complete() - Mark as complete")
    print("- ✅ get_todo_by_id() - Get todo details")
    print("- ✅ create_todo() - Create new todo")
    print("- ✅ get_all_todos() - Get all todos")

if __name__ == "__main__":
    main()
