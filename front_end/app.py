#!/usr/bin/python

import os
import io
import json
import asyncio
import uvicorn

from fastapi import FastAPI, Request, WebSocket  # ,Response, Body, Form,
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from pydantic import BaseModel
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import requests
import sqlalchemy
from sqlalchemy import create_engine, text

parent_dir_path = os.path.dirname(os.path.realpath(__file__))

POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@bravo_database/{POSTGRES_DB}')

server = FastAPI(
    title='Bravo API',
    description='Bravo API',
    docs_url=None,
    redoc_url=None)

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], )

templates = Jinja2Templates(directory="templates")
server.mount("/static", StaticFiles(directory="static"), name="static")
server.mount("/assets", StaticFiles(directory="assets"), name="assets")

@server.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=server.openapi_url,
        title=server.title + " - Swagger UI",
        oauth2_redirect_url=server.swagger_ui_oauth2_redirect_url,
        swagger_js_url=f"/static/swagger-ui-bundle.js",
        swagger_css_url=f"/static/swagger-ui.css",
    )


@server.get(server.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@server.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=server.openapi_url,
        title=server.title + " - ReDoc",
        redoc_js_url=f"/static/redoc.standalone.js",
    )


@server.get('/hello/',
            tags=['Dummy API'],
            summary="Hello World",
            description="Returns a message")
async def hello():
    return "Is it me you're looking for?"

@server.get('/math/add/{a}/{b}',
            tags=['Dummy API'],
            summary="Hello World",
            description="Returns a message")
async def mathadd(a: int, b: int):
    x = a
    y = b
    z = x + y
    return {"answer": z}

@server.get('/db/test/',
            tags=['Database API'],
            summary="Hello World",
            description="Database Timestamp")
async def hellodb():
    df = pd.read_sql_query(text('SELECT CURRENT_TIMESTAMP as "realtime_data";'), engine)
    return df.to_dict(orient='records')

# HTML test
@server.get("/", response_class=HTMLResponse,
            tags=['Webpage API'],
            summary="Home Page",
            description="Landing Page")
def index_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("app:server", host="0.0.0.0", port=80, log_level="info", reload=True)
