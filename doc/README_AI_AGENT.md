# TodoApp with AI Agent - Complete Documentation

## 🎯 Overview

**TodoApp AI Agent** là một ứng dụng quản lý công việc (Todo) được tích hợp với **AI Agent** có khả năng:

- ✅ Hiểu ngôn ngữ tự nhiên (tiếng Việt/Anh)
- ✅ Gọi các hàm (Tool-calling) tự động
- ✅ Quản lý Todo thông qua cuộc hội thoại tự nhiên
- ✅ Bảo mật & xác thực người dùng

## 🏗️ Architecture

```
┌─────────────────────┐
│   FastAPI Endpoint  │  /gemini/ask-question
│   (routers/gemini) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   TodoAgent         │  Tool-calling orchestrator
│ (agents/todo_agent) │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐    ┌──────────┐
│ LLM    │    │ Tools    │
│Gemini  │    │(CRUD ops)│
└────────┘    └──────────┘
    │             │
    └──────┬──────┘
           ▼
    ┌────────────────┐
    │  SQLAlchemy    │
    │   Database     │
    └────────────────┘
```

## 📂 Project Structure

```
ToDoApp/
├── 📄 main.py                          # FastAPI app
├── 📄 database.py                      # DB config
├── 📄 models.py                        # Models (Users, Todos)
├── 📄 utils.py                         # Utils
│
├── 📁 agents/                          # 🆕 AI Agent
│   ├── __init__.py
│   └── todo_agent.py                   # Main agent
│
├── 📁 routers/                         # API endpoints
│   ├── auth.py
│   ├── todos.py                        # Legacy CRUD
│   ├── gemini.py                       # 🔄 Updated
│   ├── users.py
│   └── admin.py
│
├── 📚 DOCUMENTATION FILES:
│   ├── README.md                       # This file
│   ├── QUICK_REFERENCE.md              # Quick start
│   ├── ARCHITECTURE.md                 # Design patterns
│   ├── AGENT_GUIDE.md                  # User guide
│   ├── TOOL_CALLING_EXPLAINED.md       # Deep dive
│   └── test_agent.py                   # Test script
```

## 🚀 Quick Start

### 1. Installation
```bash
# Already installed packages
pip install fastapi sqlalchemy langchain langchain-google-genai langgraph google-genai

# Set environment
echo "GOOGLE_API_KEY=your_key" > .env
```

### 2. Run Server
```bash
uvicorn main:app --reload
```

### 3. Test Agent
```bash
python test_agent.py
```

### 4. Use in Browser
Open: `http://localhost:8000/docs`

## 💬 Example Usage

### Scenario 1: Create Todo
**User:** "Tạo một todo về học Python với độ ưu tiên 5"

**Agent Flow:**
1. Phân tích: Người dùng muốn tạo todo
2. Gọi: `create_todo` tool
3. Kết quả: Todo được tạo với ID 1
4. Response: "✅ Tôi đã tạo todo..."

### Scenario 2: List & Filter
**User:** "Hiển thị tất cả todo của tôi"

**Agent Flow:**
1. Gọi: `get_all_todos` tool
2. Kết quả: [Todo1, Todo2, ...]
3. Response: "Bạn có N todo..."

### Scenario 3: Update & Delete
**User:** "Đánh dấu todo 1 hoàn thành rồi xóa todo 2"

**Agent Flow:**
1. Gọi: `update_todo` (id=1, complete=true)
2. Kết quả: Todo 1 updated
3. Gọi: `delete_todo` (id=2)
4. Kết quả: Todo 2 deleted
5. Response: "✅ Tôi đã..."

## 🛠️ Available Tools

### Tool: `get_all_todos`
- **Input:** Không có
- **Output:** List tất cả todo của user
- **Example:**
  ```python
  result = agent._execute_tool("get_all_todos", {}, user_id=1)
  # Returns: [{"id": 1, "title": "...", ...}]
  ```

### Tool: `get_todo`
- **Input:** `todo_id` (int)
- **Output:** Chi tiết một todo
- **Example:**
  ```python
  result = agent._execute_tool("get_todo", {"todo_id": 1}, user_id=1)
  # Returns: {"id": 1, "title": "...", ...}
  ```

### Tool: `create_todo`
- **Input:** `title`, `description`, `priority`, `complete` (optional)
- **Output:** Todo mới được tạo
- **Example:**
  ```python
  result = agent._execute_tool("create_todo", {
    "title": "Learn Python",
    "description": "Learn LangChain",
    "priority": 5
  }, user_id=1)
  ```

### Tool: `update_todo`
- **Input:** `todo_id`, `title/description/priority/complete` (optional)
- **Output:** Todo được cập nhật
- **Example:**
  ```python
  result = agent._execute_tool("update_todo", {
    "todo_id": 1,
    "complete": true
  }, user_id=1)
  ```

### Tool: `delete_todo`
- **Input:** `todo_id`
- **Output:** Confirmation
- **Example:**
  ```python
  result = agent._execute_tool("delete_todo", {"todo_id": 1}, user_id=1)
  ```

## 🔐 Security

### Authentication
- ✅ JWT token required
- ✅ User must be logged in
- ✅ Token validation in every request

### Authorization
- ✅ User can only access their own todos
- ✅ Owner check: `Todos.owner_id == user_id`
- ✅ Row-level security enforced

### Input Validation
- ✅ Pydantic models
- ✅ JSON schema validation
- ✅ Type checking

## 📊 How Agent Works

### Step 1: User Sends Message
```
User: "Tạo todo về học Python"
```

### Step 2: Agent Receives
```python
await agent.process_message(
    user_message="Tạo todo về học Python",
    user_id=1
)
```

### Step 3: Invoke LLM
```
LLM receives:
- User message
- Available tools + descriptions
- Previous context
```

### Step 4: LLM Decides
```
LLM: "Người dùng muốn tạo todo → I need to call create_todo"

LLM returns:
{
  "name": "create_todo",
  "args": {
    "title": "học Python",
    "description": "...",
    "priority": 1
  }
}
```

### Step 5: Execute Tool
```python
result = agent._execute_tool(
    "create_todo",
    {"title": "học Python", ...},
    user_id=1
)
# Database operation happens here
```

### Step 6: Feed Back to LLM
```
LLM receives tool result:
{
  "id": 1,
  "title": "học Python",
  "message": "Todo created successfully"
}
```

### Step 7: Generate Response
```
LLM: "✅ Tôi đã tạo todo thành công!
Tiêu đề: 'học Python'
ID: 1"
```

### Step 8: Return to User
```json
{
  "user": "johndoe",
  "prompt": "Tạo todo về học Python",
  "response": "✅ Tôi đã tạo todo..."
}
```

## 🧪 Testing

### Unit Test
```python
# Run test script
python test_agent.py

# Expected output:
# ✅ Tạo test user
# ✅ TodoAgent initialized
# Test 1: Create todo - PASS
# Test 2: Get all todos - PASS
# ...
```

### Integration Test
```bash
# 1. Start server
uvicorn main:app --reload

# 2. In another terminal
curl -X POST "http://localhost:8000/gemini/ask-question" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tạo todo"}'
```

## 🔍 Debugging

### Enable Debug Logging
```python
# Already in main.py
logging.basicConfig(level=logging.DEBUG, ...)
```

### Check Logs
```
2026-04-15 11:19:44,147 INFO routers.gemini User asked: "..."
2026-04-15 11:19:45,234 INFO agents.todo_agent Gọi tool: create_todo
2026-04-15 11:19:45,456 DEBUG agents.todo_agent Kết quả tool: {...}
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | No token | Login first to get token |
| Todo not found | Wrong ID | Check ID exists with `get_all_todos` |
| Error: [message] | Tool error | Check logs for detailed error |
| LLM timeout | Network issue | Retry or check API key |

## 🚀 Advanced Usage

### Add Custom Tool

Edit `agents/todo_agent.py`:

```python
def _define_tools(self):
    tools = [
        # ... existing tools ...
        {
            "name": "my_tool",
            "description": "What this does",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                },
                "required": ["param"]
            }
        }
    ]

def _execute_tool(self, tool_name: str, tool_input: dict, user_id: int) -> str:
    # ... existing code ...
    elif tool_name == "my_tool":
        # Implement here
        return json.dumps({"result": "..."})
```

### Change LLM Model

```python
# In __init__
self.llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # Change model
    temperature=0.5          # Adjust creativity
)
```

### Add System Prompt

```python
# Override model with system message
from langchain.prompts import ChatPromptTemplate

system_template = """You are a helpful Todo assistant...
Always respond in Vietnamese."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("user", "{message}")
])

self.llm_with_tools = prompt | self.llm_with_tools
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `QUICK_REFERENCE.md` | Quick start & common tasks |
| `AGENT_GUIDE.md` | User guide & examples |
| `TOOL_CALLING_EXPLAINED.md` | Deep technical explanation |
| `ARCHITECTURE.md` | Design patterns & architecture |
| `README.md` | This file - overview |

## 🔗 Dependencies

```python
# Core
fastapi==0.104+
sqlalchemy==2.0+

# AI/ML
langchain==1.2.15
langchain-core==1.3.0
langchain-google-genai==4.2.2
google-genai==1.73.1
langgraph==1.1.8

# Utilities
pydantic==2.0+
python-dotenv==1.0+
```

## 🚦 Status & Roadmap

### ✅ Completed
- [x] TodoAgent with tool-calling
- [x] Integration with Gemini LLM
- [x] CRUD tools (Create, Read, Update, Delete)
- [x] Authentication & authorization
- [x] Error handling
- [x] Comprehensive logging

### 🔄 In Progress
- [ ] Multi-turn conversations
- [ ] Conversation history storage

### 📋 Planned
- [ ] MCP Server integration
- [ ] Vector database for memory
- [ ] Streaming responses
- [ ] Tool composition
- [ ] Rate limiting
- [ ] Custom system prompts

## 💡 Tips & Tricks

### Best Practices
1. Always check `owner_id` for security
2. Use JSON for tool results
3. Add detailed tool descriptions
4. Test locally before production
5. Monitor token usage

### Performance
- Agent loop: max 5 iterations (configurable)
- Database queries: indexed by `owner_id`
- LLM calls: async supported
- Logging: controlled by level

## 🐛 Troubleshooting

### "Not authenticated"
```
→ Login first
→ Get token from /auth/token
→ Use token in Authorization header
```

### "Todo not found"
```
→ Check todo ID with /gemini/ask-question
→ Make sure you own the todo
→ Try listing all todos first
```

### Agent loops forever
```
→ Check max_iterations in todo_agent.py
→ Check tool_calls logic
→ Look at logs for details
```

## 🎓 Learning Resources

1. **Understand Tool-Calling**
   - Read: `TOOL_CALLING_EXPLAINED.md`
   - Run: `test_agent.py`
   - Explore: `agents/todo_agent.py`

2. **Design Patterns**
   - Read: `ARCHITECTURE.md`
   - Study: Dependency injection, Tool pattern

3. **Hands-On**
   - Modify tools
   - Add new functionality
   - Extend agent capabilities

## 📞 Support & Questions

- **How to use?** → Read `AGENT_GUIDE.md`
- **How it works?** → Read `TOOL_CALLING_EXPLAINED.md`
- **Architecture?** → Read `ARCHITECTURE.md`
- **Quick help?** → Read `QUICK_REFERENCE.md`
- **Test everything?** → Run `python test_agent.py`

## 📝 File Checklist

```
✅ agents/
   ✅ __init__.py
   ✅ todo_agent.py

✅ routers/
   ✅ gemini.py (updated)

✅ Documentation:
   ✅ README.md (this file)
   ✅ QUICK_REFERENCE.md
   ✅ AGENT_GUIDE.md
   ✅ TOOL_CALLING_EXPLAINED.md
   ✅ ARCHITECTURE.md

✅ Tests:
   ✅ test_agent.py
```

## 🎉 Ready to Use!

Your TodoApp is now equipped with an AI Agent! 🤖

```bash
# Start coding!
uvicorn main:app --reload
```

---

**Created:** April 21, 2026  
**Status:** ✅ Ready for Development  
**Version:** 1.0

Enjoy your AI-powered Todo App! 🚀

