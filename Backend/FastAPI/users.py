### Users API ###

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
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