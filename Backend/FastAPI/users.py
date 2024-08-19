### Users API ###

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int

users_list = [User(id=1, name="Agustín", surname="Pedrote", url="https://agus.dev", age=35),
            User(id=2, name="Antonio", surname="Román", url="https://porras.com", age=35),
            User(id=3, name="Enrique", surname="Cuevas", url="https://titis.com", age=33)]


@app.get("/users")
async def users():
    return users_list

# Path http://127.0.0.1:8000/user/1
@app.get("/user/{id}")
async def user(id: int):
    return search_user(id)

# Query http://127.0.0.1:8000/user/?id=1
@app.get("/user/")
async def user(id: int):
    return search_user(id)

def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except:
        return {"error": "No se ha encontrado el usuario"}