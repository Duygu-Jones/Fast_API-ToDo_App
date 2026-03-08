from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="TodoApp/templates")



router = APIRouter(
    prefix='/todos',
    tags=['todos']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# Dependency injection
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length= 3)
    description: str = Field(min_length= 3, max_length= 100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})

    except:
        return redirect_to_login()



@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

    except:
        return redirect_to_login()



@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

    except:
        return redirect_to_login()




### ENDPOINTS ###

# Router-Get API Endpoint
@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, 
                    db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')  # Kullanıcı doğrulanamadıysa hata
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()  # Kullanıcıya ait tüm todo'ları getir



# Get API Endpoint
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, 
                    db: db_dependency, 
                    todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')  # Auth eklendi

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first() 
        
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


# Post API Endpoint
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, 
                        db: db_dependency,
                        todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')  # Auth dogrulama eklendi
    todo_model = Todos(**todo_request.model_dump(), 
                        owner_id=user.get('id'))  # Auth gore yeni todo nesnesi oluştur
    
    db.add(todo_model)
    db.commit()
    
    
    
    
    
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, 
                        db: db_dependency,
                        todo_request: TodoRequest, # herhangi bir Path'dan once verilmelidir
                        todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')  # Kullanıcı doğrulanamadıysa hata
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()  # Güncellenecek todo'yu bul
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')  # Todo bulunamadıysa hata
    
    # "TodoRequest" "BaseModel" uzerinden gelen verileri "todo_model" parametrelerine aktar
    # En guvenli yontemdir.
    todo_model.title = todo_request.title              # Başlığı güncelle
    todo_model.description = todo_request.description  # Açıklamayı güncelle
    todo_model.priority = todo_request.priority        # Önceliği güncelle
    todo_model.complete = todo_request.complete        # Tamamlanma durumunu güncelle
    
    db.add(todo_model)                                 # Güncellenmiş todo'yu ekle
    db.commit()                                        # Değişiklikleri kaydet




    

# Path Parameter: DELETE API rotası
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, 
                    db: db_dependency, 
                    todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')     # Kullanıcı doğrulanamadıysa hata
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()                        # Silinecek todo'yu bul
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')           # Todo bulunamadıysa hata
    
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()  # Todo'yu sil
    #db.delete(todo_model) # Aynisi- todo'yu siler
    db.commit()            # Değişiklikleri kaydet