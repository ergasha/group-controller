import json
from typing import Union
from utils.db_api.sqlite import db
import uvicorn
from fastapi import FastAPI,Request
from utils.db_api.sqlite import db
app = FastAPI()
from handlers.user.admin import create_user

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/add-user")
async def add_user(request:Request):
    body = await request.body()
    user_id = json.loads(body)['user_id']
    user = db.select_user(cid=user_id)
    print(user)
    if user :
        return {'user':user}
    else:
        create_user(cid=user_id)
        return {'user':'User created successfully'}



async def run_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()