### Users API ###

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"], responses={404: {"message": "No encontrado"}})

class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int

users_list = [
    User(id=1, name="Agustín", surname="Pedrote", url="https://agus.dev", age=30),
    User(id=2, name="Antonio", surname="Román", url="https://porras.com", age=40),
    User(id=3, name="Enrique", surname="Cuevas", url="https://titis.com", age=33)
]

# POST (Agregar) - http://127.0.0.1:8000/users/
@router.post("/", response_model=User, status_code=201)
async def create_user(user: User):
    if search_user(user.id):
        raise HTTPException(status_code=409, detail="El usuario ya existe")  # 409 Conflict

    users_list.append(user)
    return user

# GET - (Leer) http://127.0.0.1:8000/users/
@router.get("/", response_model=list[User])
async def get_users():
    return users_list

# GET - (Leer) Path http://127.0.0.1:8000/users/1
@router.get("/{id}", response_model=User)
async def get_user_by_id(id: int):
    user = search_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# GET - (Leer) Query http://127.0.0.1:8000/users/search/?id=1
@router.get("/search/", response_model=User)
async def get_user_by_query(id: int):
    user = search_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# PUT - (Actualizar) http://127.0.0.1:8000/users/
@router.put("/", response_model=User)
async def update_user(user: User):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            return user
            
    raise HTTPException(status_code=404, detail="No se ha encontrado el usuario para actualizar")  # 404 Not Found

# DELETE - (Borrar) http://127.0.0.1:8000/users/1
@router.delete("/{id}")
async def delete_user(id: int):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            return {"ok": "Se ha eliminado el usuario"}
            
    raise HTTPException(status_code=404, detail="No se ha encontrado el usuario para eliminar")  # 404 Not Found

# Función para buscar un usuario por ID
def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except IndexError:
        return None
