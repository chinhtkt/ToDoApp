# TodoAgent Architecture & Design Patterns

## 📐 Project Structure

```
ToDoApp/
├── main.py                          # FastAPI app entry point
├── database.py                      # SQLAlchemy setup
├── models.py                        # DB Models (Users, Todos)
├── utils.py                         # Utility functions (get_client)
│
├── agents/                          # 🆕 AI Agent package
│   ├── __init__.py                  # Exports TodoAgent
│   └── todo_agent.py                # Main agent logic
│
├── routers/
│   ├── auth.py                      # Authentication endpoints
│   ├── todos.py                     # CRUD endpoints (legacy)
│   ├── users.py                     # User management
│   ├── admin.py                     # Admin panel
│   └── gemini.py                    # 🔄 UPDATED: Gemini AI endpoint
│
├── AGENT_GUIDE.md                   # 🆕 User guide
├── TOOL_CALLING_EXPLAINED.md        # 🆕 Detailed explanation
└── test_agent.py                    # 🆕 Test script
```

## 🏗️ Component Architecture

```
┌─────────────────────────────────────┐
│   FastAPI Router (gemini.py)        │ ← HTTP Entry Point
│   POST /gemini/ask-question         │
│   Input: prompt, user, db           │
│   Output: JSON response             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   TodoAgent (todo_agent.py)         │ ← Orchestrator
│                                     │
│  ┌─────────────────────────────┐   │
│  │  LLM Setup                  │   │
│  │  - ChatGoogleGenerativeAI   │   │
│  │  - Model: gemini-2.5-flash  │   │
│  │  - Bind tools               │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Tool Definitions           │   │
│  │  - get_all_todos            │   │
│  │  - get_todo                 │   │
│  │  - create_todo              │   │
│  │  - update_todo              │   │
│  │  - delete_todo              │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Tool Execution             │   │
│  │  _execute_tool(...)         │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Agentic Loop               │   │
│  │  process_message(...)       │   │
│  │  - Invoke LLM               │   │
│  │  - Parse tool calls         │   │
│  │  - Execute tools            │   │
│  │  - Loop until done          │   │
│  └─────────────────────────────┘   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   Database Layer (models.py)        │
│                                     │
│   Todos                             │
│   ├── id                            │
│   ├── title                         │
│   ├── description                   │
│   ├── priority (1-5)                │
│   ├── complete (boolean)            │
│   └── owner_id (FK to Users)        │
│                                     │
│   Users                             │
│   ├── id                            │
│   ├── username                      │
│   ├── email                         │
│   ├── hashed_password               │
│   └── ...other fields               │
└─────────────────────────────────────┘
```

## 🔌 Key Classes & Methods

### TodoAgent Class

```python
class TodoAgent:
    def __init__(self, db: Session):
        """Initialize with database session"""
        self.db = db
        self.llm = ChatGoogleGenerativeAI(...)
        self.tools = self._define_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
    
    def _define_tools(self) -> list[dict]:
        """Define available tools with JSON schemas"""
        # Returns list of tool definitions
    
    def _execute_tool(self, tool_name: str, tool_input: dict, user_id: int) -> str:
        """Execute a specific tool"""
        # Returns JSON result
    
    async def process_message(self, user_message: str, user_id: int) -> str:
        """Main entry point - process user message"""
        # Implements agentic loop
        # Returns final response
```

## 📊 Data Flow

### 1. Request Flow
```
HTTP Request (POST /gemini/ask-question)
    ↓
Dependency Injection (user, db)
    ↓
Validation (QuestionRequest)
    ↓
Agent Initialization
    ↓
LLM Invocation
    ↓
Tool-Calling Loop
    ↓
HTTP Response
```

### 2. Tool Execution Flow
```
Tool Call from LLM
    ↓
_execute_tool()
    ↓
Database Query
    ↓
Permission Check (owner_id)
    ↓
Operation (Create/Read/Update/Delete)
    ↓
JSON Response
    ↓
Back to LLM
```

## 🔐 Security Features

### 1. Authentication
```python
@router.post("/ask-question")
async def ask_question(
    user: user_dependency,  # ← JWT validation via get_current_user
    ...
):
```

### 2. Authorization
```python
todo = self.db.query(Todos).filter(
    Todos.id == todo_id,
    Todos.owner_id == user_id  # ← User can only access their own todos
)
```

### 3. Input Validation
```python
class QuestionRequest(BaseModel):
    prompt: str  # ← Validated by Pydantic

# Tool input validation
"priority": {
    "type": "integer",
    "minimum": 1,
    "maximum": 5  # ← Enforced by schema
}
```

## 🎯 Design Patterns Used

### 1. Dependency Injection
```python
# In router
user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

# In endpoint
async def ask_question(
    user: user_dependency,
    db: db_dependency,
    request: QuestionRequest
):
```

### 2. Tool Pattern
```python
# Define tools with JSON schema
tools = [
    {
        "name": "create_todo",
        "description": "...",
        "input_schema": {...}
    }
]

# Bind to LLM
llm_with_tools = llm.bind_tools(tools)
```

### 3. Message Passing Pattern
```python
from langchain_core.messages import HumanMessage, ToolMessage

messages = [HumanMessage(...)]
# ... agent loop ...
messages.append(ToolMessage(...))
```

### 4. State Machine Pattern
```python
# Loop states:
# 1. INVOKE_LLM → Check for tool calls
# 2. NO_TOOL_CALLS → Return response
# 3. HAS_TOOL_CALLS → Execute tools
# 4. COLLECT_RESULTS → Loop back to step 1
```

## 🚀 Performance Considerations

### 1. Database Sessions
```python
# Session management
db = SessionLocal()
try:
    # ...operations...
finally:
    db.close()  # ← Always close session
```

### 2. Tool Execution
```python
# Sequential tool execution
for tool_call in response.tool_calls:
    result = self._execute_tool(...)  # ← One at a time
    messages.append(ToolMessage(...))
```

### 3. Iteration Limits
```python
max_iterations = 5  # ← Prevent infinite loops
while iteration < max_iterations:
    # ...
```

## 🔄 Multi-Turn Conversation (Future)

```python
class ConversationManager:
    def __init__(self, user_id: int, agent: TodoAgent):
        self.user_id = user_id
        self.agent = agent
        self.messages = []  # ← Store history
    
    async def chat(self, user_message: str) -> str:
        # Add to history
        self.messages.append(HumanMessage(user_message))
        
        # Process with full history
        response = await self.agent.process_message(
            self.messages,
            self.user_id
        )
        
        # Store response
        self.messages.append(response)
        return response
```

## 🧪 Testing Strategy

### Unit Tests
```python
# Test _execute_tool() with mocked database
# Test tool parameter validation
# Test error handling
```

### Integration Tests
```python
# Test full agent loop
# Test with real database
# Test tool chaining
```

### E2E Tests
```python
# Test via HTTP endpoint
# Test with real LLM
# Test with real user workflow
```

## 📚 Dependencies

```python
# Core AI/ML
langchain==1.2.15
langchain-core==1.3.0
langchain-google-genai==4.2.2
google-genai==1.73.1

# Graph/Agent Framework
langgraph==1.1.8
langgraph-checkpoint==4.0.2

# Web Framework
fastapi
sqlalchemy

# Utilities
pydantic
python-dotenv
```

## 🎓 Learning Path

1. **Understand basics**
   - Read `TOOL_CALLING_EXPLAINED.md`
   - Read `AGENT_GUIDE.md`

2. **Run tests**
   - `python test_agent.py`
   - Check logs

3. **Explore code**
   - Read `agents/todo_agent.py`
   - Understand `_execute_tool()`
   - Understand `process_message()`

4. **Extend functionality**
   - Add more tools
   - Add custom prompts
   - Add multi-turn support

5. **Deploy**
   - Set environment variables
   - Configure LLM settings
   - Add monitoring

---

**Tạo ngày:** April 21, 2026
**Version:** 1.0
**Status:** Ready for development ✅

