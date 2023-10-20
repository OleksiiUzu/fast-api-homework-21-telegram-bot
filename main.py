from mongo_db import db
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated, Optional
from common import short_url_to_long, create_short_url

from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

#########################################
fake_users_db = db.user


def fake_hash_password(password: str):
    return 'fakehashed' + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(database, username: str):
    if username in database:
        user_dict = database[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    name = form_data.username
    user_dict = await fake_users_db.find_one({f"{name}.username": form_data.username})
    print(user_dict)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user_data = user_dict[name]
    user = UserInDB(**user_data)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

#########################################


@app.get("/", response_class=HTMLResponse)
async def read_items():
    return """
            <!DOCTYPE html>
            <html lang="en">
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width">
                <title>My Website</title>
              </head>
              <body>
              <form action="/" method="post">
                <input type="text" name="long_url" value="https://www.google.com" />
                <input type="text" name="short_url" value="" />
                <input type="submit" value="Submit" />
              </form> 
              </body>
            </html>
            """


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

@app.post("/")
async def root(long_url: Annotated[str, Form()], short_url: Optional[str] = Form(None)):
    url = await create_short_url(long_url, short_url)
    return url


@app.get("/{short_url}")
async def to_long(short_url: str):
    original_link = await short_url_to_long(short_url)
    data = await db.links.find_one({'short_url': short_url})
    if data:
        await db.redirects.insert_one({'short_url': short_url, 'owner': data['user_id']})
    return RedirectResponse(original_link)


@app.post("/{short_url}")
async def update_short_url(short_url: str, new_long_url: Annotated[str, Form()]):
    original_link = await db.links.find_one({'short_url': short_url})
    new_long_url = {'long_url': new_long_url}
    answer = await db.links.update_one({'_id': original_link['_id']}, {'$set': new_long_url})
    if answer.modified_count == 1:
        return {'short_url': short_url, 'long_url': new_long_url}
    return {'error': 'Nothing Modified'}
