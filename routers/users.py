from typing import Annotated                           # Tip belirteçleri için kullanılır
from pydantic import BaseModel, Field                  # Veri doğrulama ve modelleme için
from sqlalchemy.orm import Session                     # Veritabanı oturum yönetimi
from fastapi import APIRouter, Depends, HTTPException, Path  # FastAPI bileşenleri
from starlette import status                           # HTTP durum kodları
from ..models import Users                               # Users veritabanı modeli
from ..database import SessionLocal                      # Veritabanı oturum oluşturucu
from .auth import get_current_user                     # Kimlik doğrulama fonksiyonu
from passlib.context import CryptContext               # Şifre şifreleme ve doğrulama

router = APIRouter(
   prefix='/user',                                    # Tüm rotalar /user ile başlayacak
   tags=['user']                                      # Swagger UI'da görünecek etiket
)


def get_db():
   db = SessionLocal()                                # Yeni oturum oluştur
   try:
       yield db                                       # Oturumu çağıran koda db'yi gönder
   finally:
       db.close()                                     # İşlem bittiğinde oturumu kapat


# Dependency injection
db_dependency = Annotated[Session, Depends(get_db)]             # Veritabanı bağımlılığı
user_dependency = Annotated[dict, Depends(get_current_user)]    # Kullanıcı bağımlılığı
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')  # Şifre hashleme için bcrypt


# Users şifresini değiştirmek için veri modeli
class UserVerification(BaseModel):
   password: str                                      # Mevcut şifre
   new_password: str = Field(min_length=6)            # Yeni şifre (en az 6 karakter)


# Users bilgilerini getiren GET API rotası
@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
   if user is None:
       raise HTTPException(status_code=401, detail='Authentication Failed')     # Kullanıcı doğrulanamadıysa hata
   return db.query(Users).filter(Users.id == user.get('id')).first()            # Kullanıcı bilgilerini getir


# Users şifresini değiştiren PUT API rotası
@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, 
                            db: db_dependency,
                            user_verification: UserVerification):
   if user is None:
       raise HTTPException(status_code=401, detail='Authentication Failed')         # Kullanıcı doğrulanamadıysa hata
   
   user_model = db.query(Users).filter(Users.id == user.get('id')).first()          # Kullanıcıyı bul
   if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
       raise HTTPException(status_code=401, detail='Error on password change')      # Mevcut şifre doğru değilse hata
   
   user_model.hashed_password = bcrypt_context.hash(user_verification.new_password) # Yeni şifreyi hashle
   
   db.add(user_model)                                 # Kullanıcıyı güncelle
   db.commit()                                        # Değişiklikleri kaydet


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phonenumber(user: user_dependency, 
                            db: db_dependency,
                            phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()