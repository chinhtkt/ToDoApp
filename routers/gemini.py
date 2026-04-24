from fastapi import Depends, HTTPException, APIRouter
from typing import Annotated
from starlette import status
from routers.auth import get_current_user
from database import get_db
from agents import TodoAgent
import logging
from sqlalchemy.orm import Session
from pydantic import BaseModel

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/gemini',
    tags=['gemini'],
)

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


class QuestionRequest(BaseModel):
    """Request model for question"""
    prompt: str


@router.post("/ask-question", status_code=status.HTTP_200_OK)
async def ask_question(
    user: user_dependency,
    db: db_dependency,
    request: QuestionRequest
):
    """
    Send question to AI Agent
    
    Agent can call tools to:
    - Create new todo
    - View todo
    - Update todo
    - Delete todo
    - Get all todos
    
    Example:
    {
        "prompt": "Create a todo with title 'Learn Python' and description 'Learn LangChain' with priority 5"
    }
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided")
    
    try:
        user_id = user.get('user_id')
        prompt = request.prompt
        
        logger.info(f"User {user.get('username')} (ID: {user_id}) asked: {prompt}")
        
        # Initialize agent
        agent = TodoAgent(db)
        
        # Process message
        response = await agent.process_message(prompt, user_id)
        
        logger.info(f"Agent response: {response}")
        
        return {
            "user": user.get('username'),
            "prompt": prompt,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


