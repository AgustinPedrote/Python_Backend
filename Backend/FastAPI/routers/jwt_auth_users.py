### Users API con autorización OAuth2 JWT ###

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError # pip install python-jose
from passlib.context import CryptContext # pip install passlib[bcrypt]
from datetime import datetime, timedelta

# Configuramos el algoritmo de codificación, la duración del token y la clave secreta
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 3  # Duración del token en minutos
#openssl rand -hex 32
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"  # Clave secreta para codificar y decodificar el JWT 

# Creamos un router para la API con prefijo "/jwtauth" y etiquetado
router = APIRouter(tags=["jwtauth"],
                    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

# Instanciamos OAuth2PasswordBearer para manejar el flujo de autenticación OAuth2
oauth2 = OAuth2PasswordBearer(tokenUrl="jwt_login")

# Configuramos el contexto de Passlib para el manejo de hashing de contraseñas con bcrypt
crypt = CryptContext(schemes=["bcrypt"])


# Definimos el modelo de datos para un usuario, sin la contraseña
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


# Definimos el modelo de datos para un usuario en la base de datos, incluyendo la contraseña
class UserDB(User):
    password: str


# Simulamos una base de datos de usuarios con datos de ejemplo
users_db = {
    "agustin": {
        "username": "agustin",
        "full_name": "Agustín Pedrote",
        "email": "pedrote@prueba.com",
        "disabled": False,
        "password": "$2a$12$R9hhb2JDIQsuXueXjbBQ5e.gEsrGrcrmLIdaGsNqZkLNuG34NsOUu"  # Contraseña cifrada
    },
    "maria": {
        "username": "maria",
        "full_name": "María Barrosa",
        "email": "barrosa@prueba.com",
        "disabled": True,
        "password": "$2a$12$Zwv4bP75M2lP1C57A/M01.q3nHoCHEjS/TKlp1o6VmjAb2KQ4VfqO"  # Contraseña cifrada
    }
}

# Función para buscar un usuario en la base de datos por nombre de usuario (incluye contraseña)
def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])

# Función para buscar un usuario en la base de datos por nombre de usuario (sin contraseña)
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

# Dependencia para autenticar al usuario utilizando el token JWT
async def auth_user(token: str = Depends(oauth2)):
    # Excepción para manejo de errores de autenticación
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        # Decodificamos el token JWT para obtener el nombre de usuario
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    # Buscamos y retornamos el usuario en la base de datos
    return search_user(username)

# Dependencia para obtener el usuario actual autenticado y verificar que no esté deshabilitado
async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")

    return user

# Endpoint para el login de usuarios y generación de token JWT
@router.post("/jwt_login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Buscamos al usuario en la base de datos
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    # Verificamos la contraseña utilizando Passlib
    user = search_user_db(form.username)
    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    # Generamos el token JWT con el nombre de usuario y la fecha de expiración
    access_token = {"sub": user.username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}

    # Retornamos el token JWT codificado y el tipo de token
    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

# Endpoint para obtener los datos del usuario actual autenticado
@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
