
# utils.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import pytest
from ..routers.auth import bcrypt_context
from ..models import Todos, Users
from ..database import Base
from ..main import app

SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


engine = create_engine(SQLALCHEMY_DATABASE_URI,
                        connect_args={"check_same_thread": False},
                        poolclass=StaticPool,
                    )


TestingSessionLocal = sessionmaker(autocommit=False,
                                    autoflush=False,
                                    bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# mock user bilgilerinin oluşturulması
# test işlemleri için kullanılacak user bilgileri
def override_get_current_user():
    return {'username': 'testuser', 
            'id': 1, 
            'user_role': 'admin'}


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(title='Learn to code!', 
                    description='Need to learn everyday!',
                    priority=5, 
                    complete=False, 
                    owner_id=1)

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    #db.query(Todos).delete() # ORM ile delete (silme islemini kesinlestirmek icin)
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;")) # SQL ile delete
        connection.commit()
        # her test sonrasi test databasi temizlenmeli 


@pytest.fixture
def test_user():
    user = Users(
        username='testuser',
        email = 'test@gmail.com',
        first_name = 'TestUserName',
        last_name = 'TestUserLastname',
        hashed_password = bcrypt_context.hash('testpassword'),
        role = 'admin',
        phone_number = '(111)-111-1111'
        )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
    