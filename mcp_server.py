from mcp.server.fastmcp import FastMCP
import requests
import json

mcp = FastMCP(
    name="mcp_server",
)

# TodoApp API Base URL - Change port if needed
TODO_API_BASE = "http://localhost:8000"

# Mock weather data for testing (can be replaced with real API calls when network is available)
MOCK_WEATHER_DATA = {
    "hanoi": {"temp": 28, "condition": "Partly Cloudy", "humidity": 75},
    "ho chi minh": {"temp": 32, "condition": "Sunny", "humidity": 65},
    "da nang": {"temp": 26, "condition": "Rainy", "humidity": 85},
    "ha long": {"temp": 25, "condition": "Cloudy", "humidity": 80},
    "seoul": {"temp": 15, "condition": "Clear", "humidity": 55},
    "new york": {"temp": 18, "condition": "Partly Cloudy", "humidity": 60},
}

MOCK_CHUCK_NORRIS_JOKES = [
    "Chuck Norris doesn't read books. He stares them down until he gets the information he wants.",
    "Chuck Norris solved the Theory of Relativity without a pencil. He calculated it all in his head, and the paper and pen are still missing.",
    "When Chuck Norris does a pushup, he isn't lifting himself up, he's pushing the Earth down.",
    "Chuck Norris can slam a revolving door.",
    "Chuck Norris' first job was as a paperboy. There were no survivors.",
    "The only reason an apple a day keeps the doctor away is because the apple is written by Chuck Norris.",
    "Whoa, whoa, whoa. That's three syllables, guys. Whoa. Whoa. Whoa.",
    "Chuck Norris can write multi-threaded applications with a single thread.",
    "Chuck Norris invented the iPhone. All iPhone 5S are at Chuck Norris' house right now.",
]

# Global auth token storage
_auth_token = None

def get_auth_token():
    """Get stored authentication token"""
    return _auth_token

def set_auth_token(token):
    """Store authentication token"""
    global _auth_token
    _auth_token = token

# Helper function to make API requests to TodoApp
def make_todo_api_request(endpoint: str, method: str = "GET", data: dict = None, headers: dict = None, require_auth: bool = True):
    """Make request to TodoApp API"""
    url = f"{TODO_API_BASE}{endpoint}"
    
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    # Add authentication header if required and token available
    if require_auth and _auth_token:
        headers["Authorization"] = f"Bearer {_auth_token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}
        
        response.raise_for_status()
        
        # Try to parse JSON response
        try:
            return {"success": True, "data": response.json(), "status_code": response.status_code}
        except:
            return {"success": True, "data": response.text, "status_code": response.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to TodoApp. Make sure the server is running on port 8000"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {"error": "Authentication required. Please login first using todo_login()"}
        return {"error": f"HTTP Error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def add(a:int, b: int) -> int:
    """Adds two numbers together"""
    return a + b


@mcp.tool()
def get_current_temperature_by_city(city_name: str) -> str:
    """Get temperature by city name"""
    try:
        city_lower = city_name.lower().strip()
        
        # First, try to get real weather data from API
        try:
            url = f"https://wttr.in/{city_name}?format=j1"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            current = data["current_condition"][0]
            temp = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            humidity = current["humidity"]
            
            return f"{temp}°C - {desc} (Humidity: {humidity}%)"
        except Exception as api_error:
            # If real API fails, use mock data
            if city_lower in MOCK_WEATHER_DATA:
                weather = MOCK_WEATHER_DATA[city_lower]
                return f"{weather['temp']}°C - {weather['condition']} (Humidity: {weather['humidity']}%)"
            else:
                return f"City '{city_name}' not found. (Network unavailable - using fallback)"
        
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.resource("resource://ma_so_thue")
def get_ma_so_thue() -> str:
    """Get tax code"""
    return  "1234"


@mcp.tool()
def get_chuck_norris_joke() -> str:
    """Get a random Chuck Norris joke"""
    try:
        # Try to fetch from real API
        response = requests.get("https://api.chucknorris.io/jokes/random", timeout=5)
        response.raise_for_status()
        data = response.json()
        joke = data.get("value", "")
        if joke:
            return joke
    except Exception as api_error:
        # If real API fails, use mock data
        import random
        return random.choice(MOCK_CHUCK_NORRIS_JOKES)

# TodoApp Authentication Tools

@mcp.tool()
def todo_create_user(username: str, email: str, first_name: str, last_name: str, password: str, phone_number: str, role: str = "user") -> str:
    """Create a new user in TodoApp"""
    user_data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "phone_number": phone_number,
        "role": role
    }
    
    result = make_todo_api_request("/auth/create-user", "POST", user_data, require_auth=False)
    
    if result.get("error"):
        return f"❌ Error creating user: {result['error']}"
    
    if result.get("success"):
        return f"✅ User '{username}' created successfully! You can now login using todo_login()"
    
    return "❌ Unknown error occurred"

@mcp.tool()
def todo_login(username: str, password: str) -> str:
    """Login to TodoApp and get authentication token"""
    # OAuth2PasswordRequestForm expects form data
    import urllib.parse
    
    form_data = urllib.parse.urlencode({
        'username': username,
        'password': password
    })
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        url = f"{TODO_API_BASE}/auth/token"
        response = requests.post(url, data=form_data, headers=headers, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if access_token:
            set_auth_token(access_token)
            return f"Login successful! Authentication token saved. You can now access todos."
        else:
            return "Login failed: No token received"

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "Login failed: Invalid username or password"
        return f"Login failed: HTTP Error {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Login failed: {str(e)}"

@mcp.tool()
def create_multiple_todos(todos_data: str) -> str:
    """Create multiple todos at once. Input format: 'title1|description1|priority1;title2|description2|priority2;...'
    Priority: 1-5 (1=lowest, 5=highest). If not provided, defaults to 3.
    Example: 'Learn Python|Complete Python course|4;Build API|Create FastAPI project|5;Read docs|Study documentation|2'
    """
    try:
        # Parse the todos data
        todos_list = []
        todo_entries = todos_data.split(';')
        
        for entry in todo_entries:
            entry = entry.strip()
            if not entry:
                continue
                
            parts = entry.split('|')
            if len(parts) < 1:
                continue
                
            title = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
            priority = int(parts[2].strip()) if len(parts) > 2 and parts[2].strip().isdigit() else 3
            
            # Validate priority
            priority = max(1, min(5, priority))
            
            if title:
                todos_list.append({
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "complete": False
                })
        
        if not todos_list:
            return "No valid todos found in input data"

        # Create todos one by one
        results = []
        success_count = 0
        error_count = 0
        
        for i, todo_data in enumerate(todos_list, 1):
            result = make_todo_api_request("/todo", "POST", todo_data)
            
            if result.get("error"):
                results.append(f"Todo {i} '{todo_data['title']}': {result['error']}")
                error_count += 1
            elif result.get("success"):
                results.append(f"Todo {i} '{todo_data['title']}': Created successfully")
                success_count += 1
            else:
                results.append(f"Todo {i} '{todo_data['title']}': Unknown error")
                error_count += 1
        
        # Summary
        summary = f"\nSummary: {success_count} created, {error_count} failed\n"
        summary += "\n".join(results)
        
        return summary
        
    except Exception as e:
        return f"Error parsing todos data: {str(e)}\nFormat: 'title1|description1|priority1;title2|description2|priority2'"

@mcp.tool()
def create_quick_todos(count: int = 5) -> str:
    """Create multiple sample todos quickly. Just specify the count (default: 5)"""
    
    sample_todos = [
        {"title": "Learn Python Basics", "description": "Complete Python course from zero to hero", "priority": 4},
        {"title": "Build API with FastAPI", "description": "Create first web app project with FastAPI", "priority": 5},
        {"title": "Research Machine Learning", "description": "Read books and study Machine Learning", "priority": 3},
        {"title": "Write Documentation", "description": "Write guide documentation for MCP tools", "priority": 2},
        {"title": "Configure Docker", "description": "Setup and configure Docker for project", "priority": 3},
        {"title": "Learn Database Design", "description": "Study PostgreSQL and design database", "priority": 4},
        {"title": "Deploy Application", "description": "Deploy to AWS or Heroku", "priority": 5},
        {"title": "Write Unit Tests", "description": "Create test cases for all functions", "priority": 3},
        {"title": "Optimize Performance", "description": "Improve speed and application performance", "priority": 4},
        {"title": "Backup Data", "description": "Setup automatic backup system", "priority": 2}
    ]
    
    # Limit count to available samples
    count = min(count, len(sample_todos))
    
    results = []
    success_count = 0
    error_count = 0
    
    for i in range(count):
        todo_data = sample_todos[i].copy()
        todo_data["complete"] = False
        
        result = make_todo_api_request("/todo", "POST", todo_data)
        
        if result.get("error"):
            results.append(f"Todo {i+1} '{todo_data['title']}': {result['error']}")
            error_count += 1
        elif result.get("success"):
            results.append(f"Todo {i+1} '{todo_data['title']}': Created successfully")
            success_count += 1
        else:
            results.append(f"Todo {i+1} '{todo_data['title']}': Unknown error")
            error_count += 1
    
    # Summary
    summary = f"Quick Todos Creation\n"
    summary += f"Summary: {success_count}/{count} todos created successfully\n\n"
    summary += "\n".join(results)
    
    return summary

@mcp.tool()
def get_all_todos() -> str:
    """Get all todo items from TodoApp"""
    result = make_todo_api_request("/")
    
    if result.get("error"):
        return f"Error fetching todos: {result['error']}"

    if result.get("success"):
        todos = result["data"]
        if not todos:
            return "No todos found"

        output = "Todo List:\n"
        for todo in todos:
            status = "[DONE]" if todo.get("complete") else "[TODO]"
            priority = "[HIGH]" if todo.get("priority", 3) >= 4 else "[MEDIUM]" if todo.get("priority", 3) == 3 else "[LOW]"
            output += f"{status} {priority} [{todo.get('id', 'N/A')}] {todo.get('title', 'N/A')}\n"
            if todo.get("description"):
                output += f"    Description: {todo.get('description')}\n"
        
        return output
    
    return "Unknown error occurred"

@mcp.tool()
def todo_check_auth() -> str:
    """Check current authentication status"""
    if _auth_token:
        return "You are currently logged in. Token is available."
    else:
        return "Not logged in. Please use todo_login() to authenticate."

# TodoApp API Integration Tools

@mcp.tool()
def create_todo(title: str, description: str = "", priority: int = 3, complete: bool = False) -> str:
    """Create a new todo item in TodoApp"""
    todo_data = {
        "title": title,
        "description": description,
        "priority": priority,
        "complete": complete
    }
    
    result = make_todo_api_request("/todo", "POST", todo_data)
    
    if result.get("error"):
        return f"Error creating todo: {result['error']}"
    
    if result.get("success"):
        return f"Todo created successfully! Title: '{title}'"
    
    return "Unknown error occurred"

@mcp.tool()
def get_todo_by_id(todo_id: int) -> str:
    """Get a specific todo item by ID"""
    result = make_todo_api_request(f"/todo/{todo_id}")
    
    if result.get("error"):
        return f"Error fetching todo: {result['error']}"
    
    if result.get("success"):
        todo = result["data"]
        status = "DONE" if todo.get("complete") else "TODO"
        priority_label = "HIGH" if todo.get("priority", 3) >= 4 else "MEDIUM" if todo.get("priority", 3) == 3 else "LOW"
        
        output = f"""Todo Details:
ID: {todo.get('id', 'N/A')}
Title: {todo.get('title', 'N/A')}
Description: {todo.get('description', 'No description')}
Priority: {priority_label}
Status: {status}"""
        
        return output
    
    return "Unknown error occurred"

@mcp.tool()
def update_todo(todo_id: int, title: str = None, description: str = None, priority: int = None, complete: bool = None) -> str:
    """Update a todo item in TodoApp"""
    # Build update data with only provided fields
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if priority is not None:
        update_data["priority"] = priority
    if complete is not None:
        update_data["complete"] = complete
    
    if not update_data:
        return "No fields to update. Please provide at least one field to update."
    
    result = make_todo_api_request(f"/todo/{todo_id}", "PUT", update_data)
    
    if result.get("error"):
        return f"Error updating todo: {result['error']}"
    
    if result.get("success"):
        return f"Todo {todo_id} updated successfully!"
    
    return "Unknown error occurred"

@mcp.tool()
def delete_todo(todo_id: int) -> str:
    """Delete a todo item from TodoApp"""
    result = make_todo_api_request(f"/todo/{todo_id}", "DELETE")
    
    if result.get("error"):
        return f"Error deleting todo: {result['error']}"
    
    if result.get("success"):
        return f"Todo {todo_id} deleted successfully!"
    
    return "Unknown error occurred"

@mcp.tool()
def mark_todo_complete(todo_id: int) -> str:
    """Mark a todo item as complete"""
    return update_todo(todo_id, complete=True)

@mcp.tool()
def mark_todo_incomplete(todo_id: int) -> str:
    """Mark a todo item as incomplete"""
    return update_todo(todo_id, complete=False)

@mcp.tool()
def todo_logout() -> str:
    """Logout from TodoApp (clear authentication token)"""
    global _auth_token
    _auth_token = None
    return "Logged out successfully. Authentication token cleared."

@mcp.tool()
def get_users() -> str:
    """Get all users from TodoApp"""
    result = make_todo_api_request("/users/")
    
    if result.get("error"):
        return f"Error fetching users: {result['error']}"
    
    if result.get("success"):
        users = result["data"]
        if not users:
            return "No users found"
        
        output = "Users List:\n"
        for user in users:
            output += f"[{user.get('id', 'N/A')}] {user.get('username', 'N/A')} - {user.get('email', 'N/A')}\n"
            if user.get('first_name') or user.get('last_name'):
                output += f"    Name: {user.get('first_name', '')} {user.get('last_name', '')}\n"
        
        return output
    
    return "Unknown error occurred"

@mcp.tool()
def check_todo_app_status() -> str:
    """Check if TodoApp server is running and accessible"""
    result = make_todo_api_request("/")
    
    if result.get("error"):
        return f"TodoApp Status: Offline or not accessible\nError: {result['error']}\nMake sure to start the server with: uvicorn main:app --reload"
    
    if result.get("success"):
        return f"TodoApp Status: Online and accessible\nBase URL: {TODO_API_BASE}\nResponse: {result.get('status_code', 'N/A')}"
    
    return "Unknown status"

if __name__ == "__main__":
    import sys
    # GitHub Copilot uses stdio transport
    # When running standalone, use sse
    if len(sys.argv) > 1 and sys.argv[1] == '--sse':
        print("Listening on SSE transport...", file=sys.stderr)
        mcp.run(transport='sse')
    else:
        # Default: stdio transport (for GitHub Copilot)
        print("Listening on stdio transport...", file=sys.stderr)
        mcp.run(transport='stdio')
