from typing import Annotated                           # Tip belirteçleri için kullanılır
from pydantic import BaseModel, Field                  # Veri doğrulama ve modelleme için
from sqlalchemy.orm import Session                     # Veritabanı oturum yönetimi
from fastapi import APIRouter, Depends, HTTPException, Path  # FastAPI bileşenleri
from starlette import status                           # HTTP durum kodları
from ..models import Todos                               # Todos veritabanı modeli
from ..database import SessionLocal                      # Veritabanı oturum oluşturucu
from .auth import get_current_user                     # Kimlik doğrulama fonksiyonu


# Rota yönlendiricisi oluşturuyoruz
router = APIRouter(
    prefix='/admin',                                   # Tüm rotalar /admin ile başlayacak
    tags=['admin']                                     # Swagger UI'da görünecek etiket
    )


# Veritabanı oturumu oluşturup işlem sonunda kapatan fonksiyon
def get_db():
    db = SessionLocal()                                # Yeni oturum oluştur
    try:
        yield db                                       # Oturumu çağıran koda gönder
    finally:
        db.close()                                     # İşlem bittiğinde oturumu kapat



# Dependency injection
db_dependency = Annotated[Session, Depends(get_db)]             # Veritabanı bağımlılığı
user_dependency = Annotated[dict, Depends(get_current_user)]    # Kullanıcı bağımlılığı



#=============================== ENDPOINTS =========================================

# tum todos lari getiren GET API rotası
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')  # Kullanıcı admin değilse hata
    return db.query(Todos).all()                       # Tüm todo'ları getir (kullanıcıya filtreleme yapmadan)



# todo ID'sine göre getiren GET API rotası
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')  # Kullanıcı admin değilse hata
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()  # Silinecek todo'yu bul
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')  # Todo bulunamadıysa hata
    
    db.query(Todos).filter(Todos.id == todo_id).delete()     # Todo'yu sil (herhangi bir kullanıcının todo'sunu silebilir)
    db.commit()                                              # Değişiklikleri kaydet
    
    

# KOD AKISI:
# Bu modül, admin kullanıcılar için özel rotalar tanımlamaktadır. 
# Admin rolüne sahip kullanıcılar, sistemdeki tüm todo öğelerini görebilir 
# ve herhangi bir todo öğesini silebilirler. 
# Normal kullanıcılardan farklı olarak, admin kullanıcılar kendi oluşturdukları todo'larla sınırlı değildir. 
# Kodun akışı, öncelikle kullanıcı kimliğini ve rolünü doğrular, ardından admin yetkisini kontrol eder. 
# Sadece "admin" rolüne sahip kullanıcılar bu API rotalarına erişebilir. 
# Bu tasarım, sistemde farklı yetki seviyelerine dayalı bir erişim kontrolünü uygulamaktadır.