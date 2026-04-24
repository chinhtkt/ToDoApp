"""
Test script for TodoAgent - run with: python test_agent.py
"""
import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Users, Todos
from agents import TodoAgent
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Setup database
DATABASE_URL = "postgresql://postgres:12345678@localhost/todoapplicationdatabase"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def test_agent():
    """Test TodoAgent"""
    db = SessionLocal()
    
    try:
        # Create test user
        test_user = Users(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            hashed_password="hashed_password",
            is_active=True,
            role="user"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        user_id = test_user.id
        
        logger.info(f"Create test user: {test_user.username} (ID: {user_id})")
        
        # Initialize agent
        agent = TodoAgent(db)
        logger.info("TodoAgent initialized")
        
        # Test 1: Create todo
        print("\n" + "="*60)
        print("Test 1: Create a new todo")
        print("="*60)
        response = await agent.process_message(
            "Create a todo with title 'Learn Python' and description 'Learn LangChain' with priority 5",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 2: View all todos
        print("\n" + "="*60)
        print("Test 2: View all todos")
        print("="*60)
        response = await agent.process_message(
            "Display all my todos",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 3: Create another todo
        print("\n" + "="*60)
        print("Test 3: Create another todo")
        print("="*60)
        response = await agent.process_message(
            "Create a new task: 'Learn FastAPI' with description 'Build API' and priority 3",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 4: Update todo
        print("\n" + "="*60)
        print("Test 4: Update todo")
        print("="*60)
        response = await agent.process_message(
            "Update todo number 1, mark it as complete",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 5: View todo details
        print("\n" + "="*60)
        print("Test 5: View todo details")
        print("="*60)
        response = await agent.process_message(
            "Show me the details of todo number 2",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 6: Delete todo
        print("\n" + "="*60)
        print("Test 6: Delete todo")
        print("="*60)
        response = await agent.process_message(
            "Delete todo number 1",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 7: View all todos again
        print("\n" + "="*60)
        print("Test 7: View all todos after deletion")
        print("="*60)
        response = await agent.process_message(
            "Show me all current todos",
            user_id
        )
        print(f"Agent response: {response}\n")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    print("\nTesting TodoAgent...\n")
    asyncio.run(test_agent())
    print("\nTesting completed!")

