from mongo_db import db
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated, Optional
import uuid
from common import short_url_to_long, create_short_url

app = FastAPI()


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


@app.post("/")
async def root(long_url: Annotated[str, Form()], short_url: Optional[str] = Form(None)):
    url = await create_short_url(long_url, short_url)
    return url


@app.get("/{short_url}")
async def to_long(short_url: str):
    original_link = await short_url_to_long(short_url)
    data = await db.links.find_one({'short_url': short_url})
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