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
    """Request model cho câu hỏi"""
    prompt: str


@router.post("/ask-question", status_code=status.HTTP_200_OK)
async def ask_question(
    user: user_dependency,
    db: db_dependency,
    request: QuestionRequest
):
    """
    Gửi câu hỏi đến AI Agent
    
    Agent có thể gọi các tool để:
    - Tạo todo mới
    - Xem todo
    - Cập nhật todo
    - Xóa todo
    - Lấy tất cả todo
    
    Example:
    {
        "prompt": "Tạo một todo với tiêu đề 'Học Python' và mô tả 'Học LangChain' với độ ưu tiên 5"
    }
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided")
    
    try:
        user_id = user.get('user_id')
        prompt = request.prompt
        
        logger.info(f"User {user.get('username')} (ID: {user_id}) asked: {prompt}")
        
        # Khởi tạo agent
        agent = TodoAgent(db)
        
        # Xử lý tin nhắn
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


