#!/usr/bin/python

import plotly.express as px
import plotly
from dash import html
from dash import dcc
from dash.dependencies import Output,Input,State
import dash_bootstrap_components as dbc
import dash
import dash_auth
import plotly.graph_objs as go
import plotly.express as px
import uvicorn
import json
import asyncio
from fastapi import FastAPI, Request, Response, Body, Form, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from starlette.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

import aiofiles
import base64
import os
import io
from pydantic import BaseModel

import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
from collections import deque
# from fbprophet import Prophet

import sqlalchemy
from sqlalchemy import create_engine, text 
from sqlalchemy.types import NVARCHAR, VARCHAR, String, CHAR
from sqlalchemy.inspection import inspect
import datetime as dt


parent_dir_path = os.path.dirname(os.path.realpath(__file__))

engine = create_engine('postgresql+psycopg2://postgres:123@firefly_pg_db/postgres')

server = FastAPI(
    title='Firefly API',
    description='The goal of this API is to serve Data and ML predictions to others apps',
    docs_url=None, 
    redoc_url=None)

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], )

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


##################################################
# Example of APIs
##################################################

@server.get('/hello/',
            tags=['Dummy API'],
            summary="Hello World",
            description="Returns a message")
async def hello():
    return "Is it me you're looking for?"


@server.get('/hello/database',
            tags=["Dummy API"],
            summary="From the database",
            description="DB")
async def from_db():
    df = pd.read_sql_query(text('''SELECT 'world' as "message";'''), con=engine)
    return df.to_dict(orient='records')

@server.get('/hello/database/timestamp',
            tags=["Timestamp API"],
            summary="Timestamp from the Postgres database",
            description="DB")
async def from_db():
    df = pd.read_sql_query(text('''SELECT CURRENT_TIMESTAMP as "realtime_data";'''), con=engine)
    return df.to_dict(orient='records')

class load_filename(BaseModel):
    file_name: str 

#Load CSV Example
@server.post('/data/load/csv/', 
        tags=['Data Load'], 
        summary="Loads CSV Data",
        description="Receives CSV Filename and Uploads to PostgresDB")
async def load_csv_data(payload: load_filename):
    file_name = payload.file_name
    df = pd.read_csv(f'./data/{file_name}')
    df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

#Load Excel Example
@server.post('/data/load/excel/', 
        tags=['Data Load'], 
        summary="Loads Excel Data",
        description="Receives Excel Filename and Uploads to PostgresDB")
async def load_excel_data(payload: load_filename):
    file_name = payload.file_name
    xls = pd.ExcelFile(f'./data/{file_name}')
    for table_name in xls.sheet_names:
        df = pd.read_excel(f'./data/{file_name}', sheet_name=table_name)
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

server.mount("/src/", StaticFiles(directory="templates/ar_src"), name="static")
server.mount("/ar_models/", StaticFiles(directory="templates/ar_assets"), name="static")

templates = Jinja2Templates(directory="templates")
# AR Test
@server.get("/ar/", response_class = HTMLResponse, 
        tags=['Data Visualization'], 
        summary="AR HTML",
        description="Augmented Reality Test")
def ar(request:Request):
    return templates.TemplateResponse("ar.html", {"request": request})


@server.get("/fastdash/", response_class = HTMLResponse, 
        tags=['DashAPI'], 
        summary="DashAPI",
        description="Dash Integrated with FastAPI")
def fastdash(request:Request, title:str = 'Example'):
    
    us_cities = pd.read_csv("us-cities-top-1k.csv")
    map_fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon", hover_name="City", hover_data=["State", "Population"],
                        color_discrete_sequence=["fuchsia"])
    map_fig.update_layout(mapbox_style="open-street-map",  autosize=False, width=600)
    
    map_fig.update_layout(
        mapbox=dict(
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=32.5436893,
                lon=-117.03044908233454
                # lat=lat,
                # lon=lon
            ),
            pitch=40,
            zoom=3
        ), 
        legend_tracegroupgap=20, 
        legend_itemsizing="constant")

    map_as_string = plotly.offline.plot(map_fig, include_plotlyjs=False, output_type='div')

    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
    fig.update_layout(autosize=False)
    plot_as_string = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

    return templates.TemplateResponse("dash.html", {"request":request,"title":title, "plot": plot_as_string, "map": map_as_string})


##################################################
# Realtime Websockets
##################################################

@server.websocket("/timer")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(0.1)
        payload = pd.read_sql_query(text('''SELECT CURRENT_TIMESTAMP as "realtime_data";'''), con=engine).to_json(orient='records')
        await websocket.send_json(payload)

@server.websocket("/randomdata")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(0.1)
        payload = pd.read_sql_query(text('''SELECT 
                                (random()* (10000-1000 + 1) + 1000)::INT as a, 
                                (random()* (100-1 + 1) + 1)::INT as b,
                                (random()* (500-100 + 1) + 100)::INT as c, 
                                (random()* (2-0.10 + 1.00) + 0.10)::FLOAT  as a_change, 
                                (random()* (2-0.10 + 1.00) + 0.10)::FLOAT as b_change,
                                (random()* (2-0.10 + 1.00) + 0.10)::FLOAT  as c_change,
                                CURRENT_TIMESTAMP as last_updated;'''), con=engine).to_json(orient='records')
        await websocket.send_json(payload)

@server.websocket("/path")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(0.1)
        payload = '''{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [ -75.343, 39.984 ],
          [ -75.833, 39.284 ],
          [ -75.534, 39.123 ]
        ]
      },
      "properties": {
        "name": "Flight path 1"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [ -77.343, 35.984 ],
          [ -77.833, 35.284 ],
          [ -77.534, 35.123 ]
        ]
      },
      "properties": {
        "name": "Flight path 2"
      }
    }
  ]
}'''
        await websocket.send_json(payload)

@server.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

##################################################
# Beginning of Dash app
##################################################

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'hello': 'world'
}

app = dash.Dash(__name__, routes_pathname_prefix="/", external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.head = [
    html.Link(
        href=app.get_asset_url('favicon.ico'),
        rel='icon'
    ),
]
app.title = 'Dashboard'
navbar = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url('bah_full_logo.png'), height="35px", style={'padding': '0px 20px'})),
                    dbc.Col(dbc.NavbarBrand("Firefly", className="ml-2")),
                ],
                align="center",
            ),
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    color="#01807e",
    dark=True,
    sticky="top"
)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

def generate_card(title, long_title, value, pct_change):
    if pct_change > 0:
        pct_direction="▲"
        pct_class="card-diff-up"
    elif pct_change < 0:
        pct_direction="▼"
        pct_class="card-diff-down"
    else:
        pct_direction=""
        pct_class="card-diff-no-change"

    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(f"{title}", className="card-title"),
                    html.P(
                        f"{long_title}",
                        className="card-target",
                    ),
                    html.P(
                        f"{value}",
                        className="card-value",
                        id=f"{title.replace(' ', '-').lower()}-card-text"
                    ),
                    html.Span(
                        f"{pct_direction}",
                        className=f"{pct_class}",
                    ),
                    html.Span(
                        f" {pct_change}% change",
                        className=f"{pct_class}",
                    ),
                ]
            ),
        ],
        className="shadow p-3 mb-5 bg-white rounded",
    )
    return card

#Card row
kpirow = html.Div(dbc.Row(
    id="card-deck-id",
    children= [
            dbc.Col(generate_card("ROI","Return On Investment",'$ '+format(10000000, ',.2f'), 2.0)),
            dbc.Col(generate_card("Total","Total Investment",'$ '+format(10000000, ',.2f'), 1.0)),
            dbc.Col(generate_card("Number","Investment Volume",20, 1.0)),
    ],
    style={'padding': '25px'}
    )
    )

#Sankey Example
sankey_fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = ["A1", "A2", "B1", "B2", "C1", "C2"],
      color = "blue"
    ),
    link = dict(
      source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [2, 3, 3, 4, 4, 5],
      value = [8, 4, 2, 8, 4, 2]
  ))])

sankey_fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)

sankey_row = html.Div([
    dcc.Graph(figure=sankey_fig)
])

#Map Example
us_cities = pd.read_csv("us-cities-top-1k.csv")
# workday_people = pd.read_sql_query('''SELECT 
# "name", 
# "lat",
# "long"
# FROM PUBLIC.WORKDAY W ;''', con=engine)
map_fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon", 
                        hover_name="City", 
                        hover_data=["State", "Population"],
                        color_discrete_sequence=["fuchsia"], zoom=3, height=600)
map_fig.update_layout(mapbox_style="open-street-map")

map_row = html.Div([
    dcc.Graph(figure=map_fig)
])

#bar chart example
animals=['giraffes', 'orangutans', 'monkeys']

bar_fig = go.Figure(data=[
    go.Bar(name='SF Zoo', x=animals, y=[20, 14, 23]),
    go.Bar(name='LA Zoo', x=animals, y=[12, 18, 29])
])

bar_row = html.Div([
    dcc.Graph(figure=bar_fig)
])
#####

upload_row = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
        ]),
        style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
         },
        # Allow multiple files to be uploaded
        multiple=True
)
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
        # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df.columns = df.columns.str.strip()
            df.columns = map(str.lower, df.columns)
            df.columns = df.columns.str.replace(' ', '_')
            df.columns = df.columns.str.replace('/', '_')
            df.columns = df.columns.str.replace('(', '')
            df.columns = df.columns.str.replace(')', '')
            df.to_sql(filename.split('.csv')[0], con=engine, if_exists='replace')
        elif 'xlsx' in filename:
        # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            df.columns = df.columns.str.strip()
            df.columns = map(str.lower, df.columns)
            df.columns = df.columns.str.replace(' ', '_')
            df.columns = df.columns.str.replace('/', '_')
            df.columns = df.columns.str.replace('(', '')
            df.columns = df.columns.str.replace(')', '')
            df.to_sql(filename.split('.xlsx')[0], con=engine, if_exists='replace')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df.head(10).to_dict(orient='records')


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



line_row =  html.Div([dcc.Graph(id='line-chart', animate=True)])

app.layout = html.Div(
    children=[
        dcc.Interval(id='seconds-interval', interval=1*1000, n_intervals=0),
        navbar,
        kpirow,
        line_row,
        upload_row,
        sankey_row,
        map_row,
        bar_row,
        html.Div(id='output-data-upload'),
        ]
)

@app.callback(Output('line-chart', 'figure'), [Input("seconds-interval", "n_intervals")])
def updated_line_chart(n):    
    sql_query = f'''SELECT 
                    (random()* (10-5 + 1) + 5)::INT as a, 
                    CURRENT_TIMESTAMP as last_updated
                    UNION 
                    SELECT 
                    (random()* (10-5 + 1) + 5)::INT as a,
                    (CURRENT_TIMESTAMP - interval '1' SECOND) as last_updated
                    UNION 
                    SELECT 
                    (random()* (10-5 + 1) + 5)::INT as a,
                    (CURRENT_TIMESTAMP - interval '2' SECOND) as last_updated;'''

    df = pd.read_sql_query(text(sql_query), con=engine)
    df['last_updated']=pd.to_datetime(df['last_updated'], utc=True, unit='s')
    df.sort_values(by='last_updated', ascending=True, inplace=True)
    #df['last_updated']=pd.to_datetime(df['last_updated'], unit='s').dt.date

    t = deque(maxlen=5)
    a = deque(maxlen=5)


    t = df['last_updated']
    a = df['a'] 

    line_fig = go.Figure(data=[go.Scatter(x=t, y=a, mode='lines+markers')])

    line_fig.update_xaxes(tickangle=45, 
                tickformat="%Y-%m-%d %H:%M:%S",
                tickfont=dict(size=12), 
                range=[min(t),max(t)]
                )

    line_fig.update_yaxes(range=[0,15])

    return line_fig

      
server.mount("/", WSGIMiddleware(app.server))

if __name__ == "__main__":
    uvicorn.run("llm:server", host="0.0.0.0", port=81, log_level="info", reload=True)
