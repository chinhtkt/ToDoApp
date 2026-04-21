from fastapi import Depends, HTTPException, APIRouter
from typing import Annotated
from starlette import status
from routers.auth import get_current_user
from utils import get_client
import logging
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()




router = APIRouter(
    prefix='/gemini',
    tags=['gemini'],
)

user_dependency = Annotated[dict, Depends(get_current_user)]
client_dependency = Annotated[genai.Client, Depends(get_client)]
logger = logging.getLogger(__name__)


@router.get("/ask-question", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, client: client_dependency, prompt: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        logger.info(f"User {user.get('username')} asked: {prompt}")

        return {
            "user": user.get('username'),
            "prompt": prompt,
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calling Gemini API")


