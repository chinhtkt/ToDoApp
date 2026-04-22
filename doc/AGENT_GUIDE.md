# AI Agent cho TODO App - Hướng Dẫn Sử Dụng

## 📋 Giới thiệu

AI Agent đã được tích hợp thành công vào TodoApp! Agent này có khả năng:

1. **Hiểu ngôn ngữ tự nhiên** - Bạn có thể gửi yêu cầu bằng tiếng Việt hoặc tiếng Anh
2. **Tool-calling** - Agent có thể gọi các hàm để thực hiện thao tác trên Todo
3. **Lập luận** - Agent có thể hiểu ngữ cảnh và tự động chọn tool phù hợp

## 🛠️ Các Tool Có Sẵn

| Tool | Mô tả |
|------|-------|
| `get_all_todos` | Lấy tất cả todo của user |
| `get_todo` | Lấy một todo cụ thể theo ID |
| `create_todo` | Tạo todo mới |
| `update_todo` | Cập nhật todo hiện tại |
| `delete_todo` | Xóa một todo |

## 🚀 Cách Sử Dụng

### 1. Đăng nhập trước
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"
```

### 2. Sử dụng Agent
```bash
curl -X POST "http://localhost:8000/gemini/ask-question" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tạo một todo về học LangChain với độ ưu tiên 5"
  }'
```

## 📝 Ví Dụ Câu Lệnh

### Tạo Todo
```json
{
  "prompt": "Tạo một todo với tiêu đề 'Học Python' và mô tả 'Học LangChain' với độ ưu tiên 5"
}
```

**Agent sẽ:**
1. Phân tích câu lệnh
2. Gọi tool `create_todo` với các tham số phù hợp
3. Trả về kết quả

### Xem Tất Cả Todo
```json
{
  "prompt": "Hiển thị tất cả todo của tôi"
}
```

### Cập Nhật Todo
```json
{
  "prompt": "Cập nhật todo số 1, đánh dấu là hoàn thành"
}
```

### Xóa Todo
```json
{
  "prompt": "Xóa todo số 2"
}
```

## 🔍 Cách Hoạt Động (Luồng Execution)

```
User Message
    ↓
Agent nhận tin nhắn
    ↓
Gọi Gemini LLM với tools
    ↓
LLM phân tích → Chọn tool phù hợp
    ↓
Tool-calling Loop:
    ├─ Thực thi tool
    ├─ Lấy kết quả
    └─ Gửi kết quả lại cho LLM
    ↓
LLM tạo response cuối cùng
    ↓
Trả về cho User
```

## 📊 Architecture

```
routers/gemini.py (HTTP Endpoint)
    ↓
agents/todo_agent.py (TodoAgent Class)
    ├─ LLM: ChatGoogleGenerativeAI
    ├─ Tools: get_all_todos, get_todo, create_todo, update_todo, delete_todo
    └─ Tool-calling Loop
        ├─ Invoke LLM with tools
        ├─ Parse tool calls
        ├─ Execute tool
        └─ Return result to LLM
    ↓
models.py (Todos, Users)
    ↓
database.py (SQLAlchemy Session)
```

## 🔐 Bảo Mật

- Agent chỉ thực hiện action cho user hiện tại (`owner_id == user_id`)
- Tất cả yêu cầu đều phải có JWT token hợp lệ
- Database session được quản lý an toàn

## ✨ Những Tính Năng Tiếp Theo Có Thể Thêm

1. **MCP Server** - Để kết nối với các service bên ngoài
2. **Memory** - Lưu lại lịch sử conversation
3. **Multi-turn conversations** - Có thể follow-up câu hỏi
4. **Custom prompts** - Tùy chỉnh hành vi agent
5. **Rate limiting** - Giới hạn số lần gọi API

## 🐛 Debug

Kiểm tra logs trong console:
```
[DEBUG] Gọi tool: create_todo với input: {...}
[DEBUG] Kết quả tool: {...}
```

## 📌 Chú Ý

- Agent có giới hạn 5 lần gọi tool (max_iterations)
- Mỗi tool-call có timeout tự động
- Error handling đã được thêm vào

---

**Tạo ngày:** April 21, 2026
**Status:** Ready for testing ✅

