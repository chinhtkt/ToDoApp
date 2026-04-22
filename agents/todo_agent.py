"""
AI Agent cho Todo App - sử dụng Gemini LLM với tool-calling
"""
import json
import logging
import os
from typing import Any, Annotated
from sqlalchemy.orm import Session
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from models import Todos
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TodoRequest(BaseModel):
    """Request model cho Todo"""
    title: str
    description: str
    priority: int
    complete: bool = False


class AgentState(TypedDict):
    """State của Agent"""
    messages: Annotated[list, add_messages]
    user_id: int
    db: Session


class TodoAgent:
    """AI Agent cho quản lý Todo với tool-calling"""
    
    def __init__(self, db: Session):
        """
        Khởi tạo Agent
        
        Args:
            db: SQLAlchemy session
        """
        # Lấy API key từ environment
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY không tìm thấy trong .env file!")
        
        self.db = db
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            api_key=api_key
        )
        self.tools = self._define_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
    def _define_tools(self):
        """Định nghĩa các tool có thể gọi"""
        tools = [
            {
                "name": "get_all_todos",
                "description": "Lấy tất cả todo của user hiện tại",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_todo",
                "description": "Lấy một todo cụ thể theo ID",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "integer",
                            "description": "ID của todo"
                        }
                    },
                    "required": ["todo_id"]
                }
            },
            {
                "name": "create_todo",
                "description": "Tạo một todo mới",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Tiêu đề của todo"
                        },
                        "description": {
                            "type": "string",
                            "description": "Mô tả của todo"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Độ ưu tiên (1-5)",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "complete": {
                            "type": "boolean",
                            "description": "Trạng thái hoàn thành (mặc định: false)"
                        }
                    },
                    "required": ["title", "description", "priority"]
                }
            },
            {
                "name": "update_todo",
                "description": "Cập nhật một todo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "integer",
                            "description": "ID của todo"
                        },
                        "title": {
                            "type": "string",
                            "description": "Tiêu đề mới"
                        },
                        "description": {
                            "type": "string",
                            "description": "Mô tả mới"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Độ ưu tiên mới (1-5)"
                        },
                        "complete": {
                            "type": "boolean",
                            "description": "Trạng thái hoàn thành mới"
                        }
                    },
                    "required": ["todo_id"]
                }
            },
            {
                "name": "delete_todo",
                "description": "Xóa một todo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "integer",
                            "description": "ID của todo cần xóa"
                        }
                    },
                    "required": ["todo_id"]
                }
            }
        ]
        return tools

    def _execute_tool(self, tool_name: str, tool_input: dict, user_id: int) -> str:
        """
        Thực thi một tool
        
        Args:
            tool_name: Tên của tool
            tool_input: Input của tool
            user_id: ID của user
            
        Returns:
            Kết quả của tool (dạng string)
        """
        try:
            if tool_name == "get_all_todos":
                todos = self.db.query(Todos).filter(Todos.owner_id == user_id).all()
                todos_data = [
                    {
                        "id": todo.id,
                        "title": todo.title,
                        "description": todo.description,
                        "priority": todo.priority,
                        "complete": todo.complete
                    }
                    for todo in todos
                ]
                return json.dumps(todos_data, ensure_ascii=False)
            
            elif tool_name == "get_todo":
                todo_id = tool_input.get("todo_id")
                todo = self.db.query(Todos).filter(
                    Todos.id == todo_id,
                    Todos.owner_id == user_id
                ).first()
                if not todo:
                    return json.dumps({"error": f"Todo {todo_id} không tìm thấy"})
                return json.dumps({
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "priority": todo.priority,
                    "complete": todo.complete
                }, ensure_ascii=False)
            
            elif tool_name == "create_todo":
                new_todo = Todos(
                    title=tool_input.get("title"),
                    description=tool_input.get("description"),
                    priority=tool_input.get("priority"),
                    complete=tool_input.get("complete", False),
                    owner_id=user_id
                )
                self.db.add(new_todo)
                self.db.commit()
                self.db.refresh(new_todo)
                return json.dumps({
                    "id": new_todo.id,
                    "title": new_todo.title,
                    "description": new_todo.description,
                    "priority": new_todo.priority,
                    "complete": new_todo.complete,
                    "message": "Todo đã được tạo thành công"
                }, ensure_ascii=False)
            
            elif tool_name == "update_todo":
                todo_id = tool_input.get("todo_id")
                todo = self.db.query(Todos).filter(
                    Todos.id == todo_id,
                    Todos.owner_id == user_id
                ).first()
                if not todo:
                    return json.dumps({"error": f"Todo {todo_id} không tìm thấy"})
                
                if "title" in tool_input:
                    todo.title = tool_input["title"]
                if "description" in tool_input:
                    todo.description = tool_input["description"]
                if "priority" in tool_input:
                    todo.priority = tool_input["priority"]
                if "complete" in tool_input:
                    todo.complete = tool_input["complete"]
                
                self.db.add(todo)
                self.db.commit()
                return json.dumps({
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "priority": todo.priority,
                    "complete": todo.complete,
                    "message": "Todo đã được cập nhật thành công"
                }, ensure_ascii=False)
            
            elif tool_name == "delete_todo":
                todo_id = tool_input.get("todo_id")
                todo = self.db.query(Todos).filter(
                    Todos.id == todo_id,
                    Todos.owner_id == user_id
                ).first()
                if not todo:
                    return json.dumps({"error": f"Todo {todo_id} không tìm thấy"})
                
                self.db.delete(todo)
                self.db.commit()
                return json.dumps({
                    "message": f"Todo {todo_id} đã được xóa thành công"
                }, ensure_ascii=False)
            
            else:
                return json.dumps({"error": f"Tool '{tool_name}' không tồn tại"})
                
        except Exception as e:
            logger.error(f"Lỗi khi thực thi tool {tool_name}: {str(e)}")
            return json.dumps({"error": f"Lỗi: {str(e)}"})

    async def process_message(self, user_message: str, user_id: int) -> str:
        """
        Xử lý tin nhắn từ user
        
        Args:
            user_message: Tin nhắn của user
            user_id: ID của user
            
        Returns:
            Phản hồi từ agent
        """
        from langchain_core.messages import HumanMessage, ToolMessage
        
        messages = [HumanMessage(content=user_message)]
        logger.info(f"User {user_id} gửi: {user_message}")
        
        # Loop xử lý tool-calling
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Iteration {iteration}")
            
            # Gọi LLM
            response = self.llm_with_tools.invoke(messages)
            messages.append(response)
            
            # Kiểm tra nếu có tool calls
            if not response.tool_calls:
                # Không có tool call - return final response
                return response.content
            
            # Xử lý các tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["args"]
                tool_use_id = tool_call["id"]
                
                logger.info(f"Gọi tool: {tool_name} với input: {tool_input}")
                
                # Thực thi tool
                result = self._execute_tool(tool_name, tool_input, user_id)
                logger.debug(f"Kết quả tool: {result}")
                
                # Thêm kết quả vào messages
                messages.append(ToolMessage(
                    content=result,
                    tool_call_id=tool_use_id,
                    name=tool_name
                ))
        
        return "Đã đạt giới hạn số lần lặp lại. Vui lòng thử lại."

