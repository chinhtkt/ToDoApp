"""
Test script cho TodoAgent - chạy bằng: python test_agent.py
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
        # Tạo test user
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
        
        logger.info(f"✅ Tạo test user: {test_user.username} (ID: {user_id})")
        
        # Khởi tạo agent
        agent = TodoAgent(db)
        logger.info("✅ TodoAgent initialized")
        
        # Test 1: Tạo todo
        print("\n" + "="*60)
        print("Test 1: Tạo một todo mới")
        print("="*60)
        response = await agent.process_message(
            "Tạo một todo với tiêu đề 'Học Python' và mô tả 'Học LangChain' với độ ưu tiên 5",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 2: Xem tất cả todo
        print("\n" + "="*60)
        print("Test 2: Xem tất cả todo")
        print("="*60)
        response = await agent.process_message(
            "Hiển thị tất cả todo của tôi",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 3: Tạo todo khác
        print("\n" + "="*60)
        print("Test 3: Tạo todo khác")
        print("="*60)
        response = await agent.process_message(
            "Tạo một task mới: 'Học FastAPI' với mô tả 'Xây dựng API' và độ ưu tiên 3",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 4: Cập nhật todo
        print("\n" + "="*60)
        print("Test 4: Cập nhật todo")
        print("="*60)
        response = await agent.process_message(
            "Cập nhật todo số 1, đánh dấu là hoàn thành",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 5: Xem chi tiết một todo
        print("\n" + "="*60)
        print("Test 5: Xem chi tiết todo")
        print("="*60)
        response = await agent.process_message(
            "Cho tôi xem chi tiết của todo số 2",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 6: Xóa todo
        print("\n" + "="*60)
        print("Test 6: Xóa todo")
        print("="*60)
        response = await agent.process_message(
            "Xóa todo số 1",
            user_id
        )
        print(f"Agent response: {response}\n")
        
        # Test 7: Xem lại tất cả todo
        print("\n" + "="*60)
        print("Test 7: Xem lại tất cả todo sau khi xóa")
        print("="*60)
        response = await agent.process_message(
            "Cho tôi xem tất cả todo hiện tại",
            user_id
        )
        print(f"Agent response: {response}\n")
        
    except Exception as e:
        logger.error(f"❌ Lỗi: {str(e)}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🤖 Testing TodoAgent...\n")
    asyncio.run(test_agent())
    print("\n✅ Testing completed!")

