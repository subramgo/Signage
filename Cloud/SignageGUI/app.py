import math
import os
import pandas as pd
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dateutil.parser
from SignageManager import SignageManager
from dash.dependencies import Input, Output
import plotly.plotly as py
from plotly import graph_objs as go
import logging

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
app.config.suppress_callback_exceptions = True

signage_manager = SignageManager()

millnames = ["", " K", " M", " B", " T"] # used to convert numbers

@server.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(server.root_path, 'static'),'favicon.ico')



#returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [
            
            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id = id_value,
                className="indicator_value"
            ),
        ],
        className="two columns indicator",
        style={"marginTop": "5px", "max height": "100px",'border-radius': 10, 'border-color': '#1C4E80'},

        
)

def indicator_alt(color, text, id_value):
    return html.Div(
        [
            
            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id = id_value,
                className="indicator_value"
            ),
        ],
        className="two columns indicator_alt",
                style={"marginTop": "5px", "max height": "100px",'border-radius': 10, 'border-color': '#1C4E80'},

        
)







