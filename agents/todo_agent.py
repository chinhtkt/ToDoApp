"""
AI Agent for Todo App - using Gemini LLM with tool-calling
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
    """Request model for Todo"""
    title: str
    description: str
    priority: int
    complete: bool = False


class AgentState(TypedDict):
    """State of the Agent"""
    messages: Annotated[list, add_messages]
    user_id: int
    db: Session


class TodoAgent:
    """AI Agent for managing Todo with tool-calling"""
    
    def __init__(self, db: Session):
        """
        Initialize Agent
        
        Args:
            db: SQLAlchemy session
        """
        # Get API key from environment
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file!")
        
        self.db = db
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            api_key=api_key
        )
        self.tools = self._define_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
    def _define_tools(self):
        """Define available tools"""
        tools = [
            {
                "name": "get_all_todos",
                "description": "Get all todos of current user",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_todo",
                "description": "Get a specific todo by ID",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "integer",
                            "description": "ID of the todo"
                        }
                    },
                    "required": ["todo_id"]
                }
            },
            {
                "name": "create_todo",
                "description": "Create a new todo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the todo"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the todo"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Priority (1-5)",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "complete": {
                            "type": "boolean",
                            "description": "Completion status (default: false)"
                        }
                    },
                    "required": ["title", "description", "priority"]
                }
            },
            {
                "name": "update_todo",
                "description": "Update a todo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "integer",
                            "description": "ID of the todo"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "New priority (1-5)"
                        },
                        "complete": {
                            "type": "boolean",
                            "description": "New completion status"
                        }
                    },
                    "required": ["todo_id"]
                }
            },
            {
                "name": "delete_todo",
                "description": "Delete a todo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "integer",
                            "description": "ID of the todo to delete"
                        }
                    },
                    "required": ["todo_id"]
                }
            }
        ]
        return tools

    def _execute_tool(self, tool_name: str, tool_input: dict, user_id: int) -> str:
        """
        Execute a tool

        Args:
            tool_name: Name of the tool
            tool_input: Input for the tool
            user_id: User ID

        Returns:
            Tool result (as string)
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
                    return json.dumps({"error": f"Todo {todo_id} not found"})
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
                    "message": "Todo created successfully"
                }, ensure_ascii=False)
            
            elif tool_name == "update_todo":
                todo_id = tool_input.get("todo_id")
                todo = self.db.query(Todos).filter(
                    Todos.id == todo_id,
                    Todos.owner_id == user_id
                ).first()
                if not todo:
                    return json.dumps({"error": f"Todo {todo_id} not found"})

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
                    "message": "Todo updated successfully"
                }, ensure_ascii=False)
            
            elif tool_name == "delete_todo":
                todo_id = tool_input.get("todo_id")
                todo = self.db.query(Todos).filter(
                    Todos.id == todo_id,
                    Todos.owner_id == user_id
                ).first()
                if not todo:
                    return json.dumps({"error": f"Todo {todo_id} not found"})

                self.db.delete(todo)
                self.db.commit()
                return json.dumps({
                    "message": f"Todo {todo_id} deleted successfully"
                }, ensure_ascii=False)
            
            else:
                return json.dumps({"error": f"Tool '{tool_name}' does not exist"})

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return json.dumps({"error": f"Error: {str(e)}"})

    async def process_message(self, user_message: str, user_id: int) -> str:
        """
        Process user message

        Args:
            user_message: User message
            user_id: User ID

        Returns:
            Agent response
        """
        from langchain_core.messages import HumanMessage, ToolMessage

        messages = [HumanMessage(content=user_message)]
        logger.info(f"User {user_id} sent: {user_message}")

        # Loop to process tool-calling
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Iteration {iteration}")
            
            # Call LLM
            response = self.llm_with_tools.invoke(messages)
            messages.append(response)
            
            # Check for tool calls
            if not response.tool_calls:
                # No tool call - return final response
                return response.content
            
            # Process tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["args"]
                tool_use_id = tool_call["id"]
                
                logger.info(f"Calling tool: {tool_name} with input: {tool_input}")

                # Execute tool
                result = self._execute_tool(tool_name, tool_input, user_id)
                logger.debug(f"Tool result: {result}")

                # Add result to messages
                messages.append(ToolMessage(
                    content=result,
                    tool_call_id=tool_use_id,
                    name=tool_name
                ))
        
        return "Maximum iterations reached. Please try again."

