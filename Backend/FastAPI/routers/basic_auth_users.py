### Users API con autorización OAuth2 básica ###

# Importación de módulos y dependencias necesarias
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(
    # prefix="/basicauth",
    tags=["basicauth"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}  # Respuesta personalizada para 404
)

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Este modelo representa los datos públicos del usuario (excluye la contraseña)
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

# Definición del modelo 'UserDB', que extiende 'User' e incluye la contraseña
class UserDB(User):
    password: str

# Base de datos 
users_db = {
    "agusdev": {
        "username": "agusdev",
        "full_name": "Agustín Pedrote",
        "email": "agusdev@hotmail.com",
        "disabled": False,
        "password": "123456"
    },
    "periquito": {
        "username": "periquito",
        "full_name": "Periquito Perez",
        "email": "Periquito@gmail.es",
        "disabled": True,
        "password": "654321"
    }
}

# Función que busca un usuario en la base de datos por nombre de usuario
# Si se encuentra, se devuelve una instancia de UserDB (incluyendo la contraseña)
def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])

# Función que busca un usuario en la base de datos por nombre de usuario
# Si se encuentra, se devuelve una instancia de User (sin incluir la contraseña)
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

# Dependencia que obtiene el usuario actual a partir del token proporcionado
async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )

    return user

# Valida las credenciales (nombre de usuario y contraseña) enviadas en el formulario
# Si son correctas, devuelve un token de acceso con el nombre de usuario
# http://127.0.0.1:8000/login
# Body / Form -> username, password
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Busca el usuario en la base de datos
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto"
        )

    # Verifica que la contraseña sea correcta
    user = search_user_db(form.username)
    if not form.password == user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta"
        )

    # Devuelve el token de acceso en caso de éxito
    return {"access_token": user.username, "token_type": "bearer"}

# Endpoint GET para obtener el perfil del usuario actual (/basicauth/users/me)
# Utiliza la dependencia 'current_user' para autenticar al usuario mediante el token
# Devuelve los datos del usuario autenticado
# http://127.0.0.1:8000/users/me
# Auth / Bearer -> token(agusdev)
@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
