import os
import motor
from motor import motor_asyncio
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated, Optional


import uuid

app = FastAPI()

client = motor_asyncio.AsyncIOMotorClient('mongodb://root:example@localhost:27017')
db = client.short_link

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

    if short_url:
        exists_short_url = await db.links.find_one({'short_url': short_url})
        if exists_short_url:
            return {'error': 'short link already created'}
    else:
        short_url = str(uuid.uuid4())
    new_link = await db.links.insert_one({'short_url': short_url, 'long_url': long_url})
    return short_url


@app.get("/{short_url}")
async def to_long(short_url: str):
    original_link = await db.links.find_one({'short_url': short_url})
    return RedirectResponse(original_link['long_url'])


@app.post("/{short_url}")
async def update_short_url(short_url: str, new_long_url: Annotated[str, Form()]):
    original_link = await db.links.find_one({'short_url': short_url})
    new_long_url = {'long_url': new_long_url}
    answer = await db.links.update_one({'_id': original_link['_id']}, {'$set': new_long_url})
    if answer.modified_count == 1:
        return {'short_url': short_url, 'long_url': new_long_url}
    return {'error': 'Nothing Modified'}