from fastapi import FastAPI, Request, status
from .models import Base
from .database import engine     # Veritabanı motoru nesnesini içe aktarıyoruz
from .routers import auth, todos, admin, users  # Her bir modulde olsuturulan Yönlendiricileri içe aktarıyoruz
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse



app = FastAPI()  # FastAPI uygulaması oluşturuyoruz

# Tanımlanan tüm modelleri "Base" sayesinde veritabanında tablo olarak oluşturuyoruz
Base.metadata.create_all(bind=engine)



app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")

@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


# test_main.py icin health_check fonksiyonunu tanımlıyoruz
@app.get("/healthy")  # Uygulamanın sağlığını kontrol etmek için bir rotayı tanımla
def health_check():
    return {'status': 'Healthy'}  # Sağlıklı olduğuna dair bir mesaj 


app.include_router(auth.router)  # Kimlik doğrulama rotalarını ekliyoruz
app.include_router(todos.router)  # Yapılacaklar listesi rotalarını ekliyoruz
app.include_router(admin.router)  # Yönetici rotalarını ekliyoruz
app.include_router(users.router)  # Kullanıcı yönetimi rotalarını ekliyoruz

