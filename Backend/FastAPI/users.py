### Users API ###

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int

users_list = [User(id=1, name="Agustín", surname="Pedrote", url="https://agus.dev", age=30),
            User(id=2, name="Antonio", surname="Román", url="https://porras.com", age=40),
            User(id=3, name="Enrique", surname="Cuevas", url="https://titis.com", age=33)]

# GET
@app.get("/users")
async def users():
    return users_list

# Path http://127.0.0.1:8000/user/1
@app.get("/user/{id}")
async def user(id: int):
    user = search_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Query http://127.0.0.1:8000/user/?id=1
@app.get("/user/")
async def user(id: int):
    user = search_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") 
    return user

# POST http://127.0.0.1:8000/user/
@app.post("/user/", response_model=User, status_code=201)
async def user(user: User):
    if search_user(user.id):
        raise HTTPException(status_code=409, detail="El usuario ya existe") # 409 Conflict

    users_list.append(user)
    return user

# PUT http://127.0.0.1:8000/user/
@app.put("/user/", response_model=User)
async def user(user: User):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            return user
            
    raise HTTPException(status_code=404, detail="No se ha encontrado el usuario para actualizar")  # 404 Not Found

# DELETE http://127.0.0.1:8000/user/1
@app.delete("/user/{id}")
async def user(id: int):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            return {"ok": "Se ha eliminado el usuario"}
            
    raise HTTPException(status_code=404, detail="No se ha encontrado el usuario para eliminar")  # 404 Not Found
    
# Busqueda del usuario
def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except IndexError:
        return None
    
    