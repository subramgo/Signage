# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import plotly.plotly as py
from plotly import graph_objs as go
import math
from app import app, server, signage_manager
from apps import snapshot, live
import logging

"""
Color Scheme

 HEX color codes used: #F1F1F1, #202020, #7E909A, #1C4E80, #A5D8DD, #EA6A47, #0091D5

"""



tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'

}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#1C4E80',
    'color': 'white',
    'padding': '6px'
}
app.layout = html.Div(
    [


        #html.Link(href="static/all.css",rel="stylesheet"),
        html.Link(href="static/all.min.css",rel="stylesheet"),

        #html.Link(href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",rel="stylesheet"),
        html.Link(href="static/stylesheet-oil-and-gas.css",rel="stylesheet"),

        html.Link(href="static/Dosis.css", rel="stylesheet"),
        html.Link(href="static/OpenSan.css", rel="stylesheet"),
        html.Link(href="static/Ubuntu.css", rel="stylesheet"),
        #html.Link(href="https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css", rel="stylesheet"),
        html.Link(href="static/dash_crm.css", rel="stylesheet"),


        # header
        html.Div([

            html.Span("Smart Signage", className='app-title'),
            
            html.Div(
                html.Img(src='./static/logo.png',height="80%")
                ,style={"float":"right","height":"80%","margin":"1% 1%"})
            ],
            className="row header"
            ),

        #tabs
        html.Div([

            dcc.Tabs(
                id="tabs",
                value="live_tab",
        #parent_className='custom-tabs',
        #className='custom-tabs-container',
                children=[
                    dcc.Tab(label="Single Signage View", value="live_tab",style=tab_style, selected_style=tab_selected_style),
                    
                    dcc.Tab(label="Compare Signages", value="snapshot_tab",style=tab_style, selected_style=tab_selected_style)
                ]
            ,style=tabs_styles)

            ],
            className="row",style={"margin": "2% 3%"}
        ),
  

        html.Div(
                signage_manager.get_first_row_header().to_json(orient='split'),
                id="snapshot_df",
                style={"display": "none"},
        ),

 


         html.Div(id="tab_content", className="row", style={"margin": "2% 3%"})
        
    ],
    className="row",
    style={"margin": "0%"},
)

@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "snapshot_tab":
        return snapshot.layout
    elif tab == "live_tab":
        return live.layout


