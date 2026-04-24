# Visual Diagrams - TodoAgent Flow

## 1. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    User/Client                                │
│              (Browser, cURL, Mobile App)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTP POST
                         │ /gemini/ask-question
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  FastAPI Server                               │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  routers/gemini.py                                     │ │
│  │  - ask_question() endpoint                             │ │
│  │  - user_dependency (JWT check)                         │ │
│  │  - db_dependency (SQLAlchemy session)                  │ │
│  └────────────────────────┬─────────────────────────────┘ │
│                           │                                 │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  agents/todo_agent.py                                  │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ TodoAgent Class                                │ │ │
│  │  │                                                │ │ │
│  │  │ ┌────────────────────────────────────────────┐ │ │ │
│  │  │ │ LLM Integration                            │ │ │ │
│  │  │ │ - ChatGoogleGenerativeAI                   │ │ │ │
│  │  │ │ - model: gemini-2.5-flash                  │ │ │ │
│  │  │ │ - bind_tools(...)                          │ │ │ │
│  │  │ └────────────────────────────────────────────┘ │ │ │
│  │  │                                                │ │ │
│  │  │ ┌────────────────────────────────────────────┐ │ │ │
│  │  │ │ Tool Definitions                           │ │ │ │
│  │  │ │ 1. get_all_todos                           │ │ │ │
│  │  │ │ 2. get_todo                                │ │ │ │
│  │  │ │ 3. create_todo                             │ │ │ │
│  │  │ │ 4. update_todo                             │ │ │ │
│  │  │ │ 5. delete_todo                             │ │ │ │
│  │  │ └────────────────────────────────────────────┘ │ │ │
│  │  │                                                │ │ │
│  │  │ ┌────────────────────────────────────────────┐ │ │ │
│  │  │ │ Tool Executor                              │ │ │ │
│  │  │ │ _execute_tool(...)                         │ │ │ │
│  │  │ │ - Parse tool call                          │ │ │ │
│  │  │ │ - Verify owner_id                          │ │ │ │
│  │  │ │ - Execute database op                      │ │ │ │
│  │  │ │ - Return JSON result                       │ │ │ │
│  │  │ └────────────────────────────────────────────┘ │ │ │
│  │  │                                                │ │ │
│  │  │ ┌────────────────────────────────────────────┐ │ │ │
│  │  │ │ Agentic Loop                               │ │ │ │
│  │  │ │ process_message(...)                       │ │ │ │
│  │  │ │                                            │ │ │ │
│  │  │ │ while iteration < 5:                       │ │ │ │
│  │  │ │   1. invoke LLM                            │ │ │ │
│  │  │ │   2. check tool_calls                      │ │ │ │
│  │  │ │   3. execute tools                         │ │ │ │
│  │  │ │   4. feed back to LLM                      │ │ │ │
│  │  │ │   5. if no calls → return response         │ │ │ │
│  │  │ └────────────────────────────────────────────┘ │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────┬────────────────────────────────────────┘ │
│               │                                          │
│               ▼                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Database Layer                                    │ │
│  │  - SQLAlchemy ORM                                  │ │
│  │  - models.Todos                                    │ │
│  │  - models.Users                                    │ │
│  │  - Database session management                     │ │
│  └────────────────────────────────────────────────────┘ │
│               │                                          │
└───────────────┼──────────────────────────────────────────┘
                │
                ▼
         ┌─────────────┐
         │  SQLite DB  │
         │ (or other)  │
         └─────────────┘
```

## 2. Detailed Agent Loop Flow

```
START: User sends message
│
├─ "Tạo todo về học Python với độ ưu tiên 5"
│
▼
┌─────────────────────────────────────────────┐
│ STEP 1: Initialize                          │
│ - Create TodoAgent(db)                      │
│ - Setup LLM with tools                      │
│ - Create messages list                      │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ STEP 2: First LLM Invocation                │
│                                              │
│ Input to LLM:                               │
│ • Message: "Tạo todo về học Python..."     │
│ • Tools: [schema for 5 tools]              │
│ • User ID: 1                                │
│                                              │
│ LLM Analysis:                               │
│ "User wants to CREATE a todo                │
│  → I need to call create_todo tool"         │
│                                              │
│ LLM Output:                                 │
│ {                                            │
│   "tool_calls": [                           │
│     {                                        │
│       "id": "tool_use_123",                 │
│       "name": "create_todo",                │
│       "args": {                             │
│         "title": "Học Python",              │
│         "description": "Học Python...",     │
│         "priority": 5                       │
│       }                                      │
│     }                                        │
│   ]                                          │
│ }                                            │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ STEP 3: Check for Tool Calls                │
│                                              │
│ if response.tool_calls:                     │
│   → Yes, proceed to execution               │
│ else:                                        │
│   → No, return LLM response                 │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ STEP 4: Execute Tool                        │
│                                              │
│ _execute_tool("create_todo", {              │
│   "title": "Học Python",                    │
│   "description": "Học Python...",           │
│   "priority": 5                             │
│ }, user_id=1)                               │
│                                              │
│ Database Operations:                        │
│ 1. Create Todos instance                    │
│ 2. Set owner_id = 1                         │
│ 3. db.add() + db.commit()                   │
│ 4. db.refresh() to get ID                   │
│                                              │
│ Return: {                                    │
│   "id": 15,                                  │
│   "title": "Học Python",                    │
│   "description": "Học Python...",           │
│   "priority": 5,                            │
│   "complete": false,                        │
│   "message": "Todo đã được tạo..."          │
│ }                                            │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ STEP 5: Add Result to Messages              │
│                                              │
│ messages.append(ToolMessage(                │
│   content=json.dumps(result),               │
│   tool_use_id="tool_use_123",              │
│   name="create_todo"                        │
│ ))                                           │
│                                              │
│ Messages now contain:                       │
│ 1. HumanMessage (original)                  │
│ 2. AIMessage (tool calls)                   │
│ 3. ToolMessage (results) ← NEW             │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ STEP 6: Second LLM Invocation               │
│                                              │
│ Input to LLM:                               │
│ • Full message history (all 3 messages)    │
│ • Tool schemas (again)                      │
│                                              │
│ LLM Analysis:                               │
│ "Tool executed successfully!                │
│  Todo with ID 15 was created.               │
│  No more tools needed.                      │
│  Generate user-friendly response"           │
│                                              │
│ LLM Output:                                 │
│ {                                            │
│   "content": "✅ Tôi đã tạo todo thành     │
│   công! Tiêu đề: 'Học Python'...           │
│   ID: 15",                                  │
│   "tool_calls": null  ← NO MORE CALLS      │
│ }                                            │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ STEP 7: Check Again for Tool Calls          │
│                                              │
│ if not response.tool_calls:                 │
│   → No more tools → EXIT LOOP               │
│   return response.content                   │
│                                              │
│ Response: "✅ Tôi đã tạo todo thành..."    │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ STEP 8: Return to HTTP Endpoint             │
│                                              │
│ {                                            │
│   "user": "johndoe",                        │
│   "prompt": "Tạo todo về học Python...",   │
│   "response": "✅ Tôi đã tạo todo..."       │
│ }                                            │
└─────────────────────────────────────────────┘
│
▼
HTTP Response (200 OK)
│
▼
END: User receives response
```

## 3. Multi-Tool Execution Example

```
Scenario: "Tạo 2 todo rồi hiển thị tất cả"

┌─────────────────────────────────────────────┐
│ Iteration 1: Create First Todo              │
├─────────────────────────────────────────────┤
│ Tool Call: create_todo(...)                 │
│ Tool Result: {id: 1, ...}                   │
│ Messages: [Human, AI, Tool]                 │
│ Loop continues (has tool_calls) → Iter 2    │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ Iteration 2: Create Second Todo             │
├─────────────────────────────────────────────┤
│ Tool Call: create_todo(...)                 │
│ Tool Result: {id: 2, ...}                   │
│ Messages: [Human, AI, Tool, AI, Tool]       │
│ Loop continues (has tool_calls) → Iter 3    │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ Iteration 3: Get All Todos                  │
├─────────────────────────────────────────────┤
│ Tool Call: get_all_todos()                  │
│ Tool Result: [{id:1,...}, {id:2,...}]       │
│ Messages: [Human, AI, Tool, AI, Tool, ..] │
│ Loop continues (has tool_calls) → Iter 4    │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ Iteration 4: Generate Final Response        │
├─────────────────────────────────────────────┤
│ No Tool Call (tool_calls = null)            │
│ LLM response: "✅ I created 2 todos..."     │
│ EXIT LOOP                                   │
└─────────────────────────────────────────────┘
│
▼
Return: "✅ I created 2 todos and here they are: ..."
```

## 4. Security Flow

```
┌──────────────────────────────────┐
│ Incoming Request                 │
│ POST /gemini/ask-question        │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ LAYER 1: JWT Validation          │
│ - Extract token from header      │
│ - Verify signature               │
│ - Get user_id                    │
└────────────┬─────────────────────┘
             │
             ▼ (if valid)
┌──────────────────────────────────┐
│ LAYER 2: Input Validation        │
│ - Parse JSON body                │
│ - Validate QuestionRequest       │
│ - Pydantic checks                │
└────────────┬─────────────────────┘
             │
             ▼ (if valid)
┌──────────────────────────────────┐
│ LAYER 3: Agent Execution         │
│ - Pass authenticated user_id     │
│ - Pass database session          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ LAYER 4: Tool Execution          │
│ - Check owner_id == user_id      │
│ - Only allow own todos           │
│ - SQL injection prevention       │
│   (SQLAlchemy ORM)               │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Database Operation               │
│ - Secure query execution         │
│ - Transaction committed          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Return Response                  │
│ - Only user's own data           │
│ - JSON formatted                 │
└──────────────────────────────────┘
```

## 5. Tool Definition Schema

```
Each tool has this structure:

┌─────────────────────────────────────────────────────┐
│ Tool Definition (JSON Schema)                       │
├─────────────────────────────────────────────────────┤
│ {                                                    │
│   "name": "create_todo",                           │
│   "description": "Tạo một todo mới",              │
│   "input_schema": {                                │
│     "type": "object",                              │
│     "properties": {                                │
│       "title": {                                    │
│         "type": "string",                          │
│         "description": "Tiêu đề của todo"         │
│       },                                            │
│       "description": {                             │
│         "type": "string",                          │
│         "description": "Mô tả của todo"           │
│       },                                            │
│       "priority": {                                │
│         "type": "integer",                         │
│         "minimum": 1,                              │
│         "maximum": 5,                              │
│         "description": "Độ ưu tiên (1-5)"        │
│       },                                            │
│       "complete": {                                │
│         "type": "boolean",                         │
│         "description": "Trạng thái hoàn thành"   │
│       }                                             │
│     },                                              │
│     "required": ["title", "description",           │
│                  "priority"]                       │
│   }                                                 │
│ }                                                   │
└─────────────────────────────────────────────────────┘

         ↓ (passed to LLM)
         
┌─────────────────────────────────────────────────────┐
│ LLM Understanding                                   │
├─────────────────────────────────────────────────────┤
│ • Tool name: create_todo                           │
│ • What it does: Creates a new todo                │
│ • Required inputs: title, description, priority   │
│ • Optional inputs: complete                       │
│ • Type constraints: int (1-5), string, boolean   │
└─────────────────────────────────────────────────────┘

         ↓ (when needed)
         
┌─────────────────────────────────────────────────────┐
│ LLM Decision                                        │
├─────────────────────────────────────────────────────┤
│ "User wants to create a todo"                      │
│ ↓                                                   │
│ "I need to call create_todo with:"                 │
│ • title: "Học Python"                              │
│ • description: "Học LangChain framework"          │
│ • priority: 5                                      │
└─────────────────────────────────────────────────────┘
```

## 6. Message Flow in Agent Loop

```
Initial State:
messages = []

After Step 1 (Human message added):
messages = [
  HumanMessage(content="Tạo todo về học Python")
]

After Step 2 (LLM response with tool call):
messages = [
  HumanMessage(content="Tạo todo về học Python"),
  AIMessage(
    content="",
    tool_calls=[{id: "123", name: "create_todo", args: {...}}]
  )
]

After Step 3 (Tool result added):
messages = [
  HumanMessage(...),
  AIMessage(...),
  ToolMessage(
    content="{\"id\": 15, \"title\": \"Học Python\", ...}",
    tool_use_id="123",
    name="create_todo"
  )
]

After Step 4 (Final LLM response):
messages = [
  HumanMessage(...),
  AIMessage(...),
  ToolMessage(...),
  AIMessage(
    content="✅ Tôi đã tạo todo thành công!...",
    tool_calls=None  # ← EXIT CONDITION
  )
]

Final Output:
"✅ Tôi đã tạo todo thành công!..."
```

---

**These diagrams represent the complete flow of the TodoAgent system!**

