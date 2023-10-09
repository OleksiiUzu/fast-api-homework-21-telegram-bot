from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing_extensions import Annotated


import uuid

app = FastAPI()

dict_urls = {}


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
                <input type="submit" value="Submit" />
              </form> 
              </body>
            </html>
            """


@app.post("/")
async def root(long_url: Annotated[str, Form()]):
    short_url = str(uuid.uuid4())
    dict_urls[short_url] = long_url
    return short_url


@app.get("/{short_url}")
async def say(short_url: str):
    return RedirectResponse(dict_urls[short_url])
