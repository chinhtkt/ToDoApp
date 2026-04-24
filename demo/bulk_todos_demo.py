#!/usr/bin/env python3
"""
Demo script for bulk create todos
"""

from mcp_server import (
    todo_login,
    create_multiple_todos,
    create_quick_todos,
    get_all_todos
)

def main():
    print("Demo Bulk Create Todos")
    print("=" * 60)
    
    # Login first
    print("\n[1] Login...")
    login_result = todo_login('demo_user', 'demo123')
    print(login_result)
    
    # Method 1: Quick todos (predefined samples)
    print("\n[2] Create 5 quick todos with create_quick_todos()...")
    quick_result = create_quick_todos(5)
    print(quick_result)
    
    # Method 2: Custom todos with create_multiple_todos()
    print("\n[3] Create 5 custom todos with create_multiple_todos()...")
    custom_todos = 'Learn React|Create web app with React|4;Learn NodeJS|Backend development with NodeJS|5;Understand Redux|State management for React|3;Write tech blog|Share programming knowledge|2;Setup CI/CD|Automatic deploy with GitHub Actions|4'
    custom_result = create_multiple_todos(custom_todos)
    print(custom_result)
    
    # Show all todos
    print("\n[4] Display all todos...")
    todos_result = get_all_todos()
    print(todos_result)
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("\nMethods to create multiple todos:")
    print("1. create_quick_todos(count) - Create predefined sample todos")
    print("2. create_multiple_todos(data) - Create custom todos")
    print("   Format: 'title1|description1|priority1;title2|description2|priority2'")

if __name__ == "__main__":
    main()
