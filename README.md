# FastAPI URL Shortener
 This is a simple URL shortener built with FastAPI as a homework project.
 Implemented telegram bot for the project

## Features
- Added Bot.py
## Installation
Clone the repository:
  ```bash
  git clone https://github.com/OleksiiUzu/fast-api-homework-21-telegram-bot.git
  cd fast-api-homework-21-telegram-bot
  ```
Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
Run the application:
  ```bash
  uvicorn main:app --reload
  ```
## Usage
Open http://127.0.0.1:8000/ in your browser to access the form.
Submit a long URL to get a shortened version.
Use the generated short URL to be redirected to the original link.

Add your telegram bot token to the "bot = AsyncTeleBot('')" in Bot.py file
