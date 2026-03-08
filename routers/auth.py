from datetime import datetime, timedelta, timezone
from fastapi import APIRouter,Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated
from pydantic import BaseModel
from ..database import SessionLocal
from ..models import Users         #class User from models.py
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


SECRET_KEY = "87be826dc02063d8e4e674e9fcf7d0874a9cbda1e0790f306d470a75065b4cdc"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') 


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str
    

class Token(BaseModel):
    access_token: str
    token_type: str


# Veritabanı bağlantısı oluşturup işlem sonunda kapatan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# Dependency injection
db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="TodoApp/templates")


### Pages ###

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})



### EndPoints ###

# Users kimlik doğrulama fonksiyonu
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()  # Kullanıcıyı veritabanında arıyoruz
    if not user:
        return False                                 # Kullanıcı bulunamadıysa False dön
    if not bcrypt_context.verify(password, user.hashed_password):  # Şifreyi kontrol ediyoruz
        return False                                 # Şifre eşleşmiyorsa False dön
    return user                                      # Doğrulama başarılıysa kullanıcı nesnesini dön




def create_access_token(username: str,      # Payload içeriği
                        user_id: int, 
                        role: str, 
                        expires_delta: timedelta):
    
    encode = {  'sub': username,            # Payload içeriği encode edilir
                'id': user_id, 
                'role': role}  
    
    expires = datetime.now(timezone.utc) + expires_delta     # Token son kullanma tarihi
    encode.update({'exp': expires})                          # Son kullanma tarihini ekle
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode edilen Token oluştur ve döndür



async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Token'ı çözümlüyoruz
        username: str = payload.get('sub')                              # Kullanıcı adını alıyoruz
        user_id: int = payload.get('id')                                # Kullanıcı ID'sini alıyoruz
        user_role: str = payload.get('role')                            # Kullanıcı rolünü alıyoruz
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')       # Geçersiz token hatası
        return {'username': username, 'id': user_id, 'user_role': user_role}  # Kullanıcı bilgilerini döndür
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')           # Token çözümlenemezse hata




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                    create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        phone_number = create_user_request.phone_number
        )
    
    db.add(create_user_model)
    db.commit()
    
    
    

# Token alma endpoint'i
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                db: db_dependency):
    
    user = authenticate_user(form_data.username, form_data.password, db)  # Kullanıcıyı doğruluyoruz
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')           # Doğrulama başarısızsa hata
    
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))  # 20 dakikalık token
    return {'access_token': token, 'token_type': 'bearer'}               # Token yanıtını döndürüyoruz 
    
    
