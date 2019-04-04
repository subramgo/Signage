# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.plotly as py
from plotly import graph_objs as go
import math
from app import app, server, signage_manager, app_state
from apps import snapshot, live, filter
from apps.insights import overall, recommendations , demographics
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
enterprise_drops = signage_manager.get_enterprise()

logging.info(app_state.print())
"""
Color Scheme

 HEX color codes used: #F1F1F1, #202020, #7E909A, #1C4E80, #A5D8DD, #EA6A47, #0091D5

"""

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '2px',
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


        html.Link(href="./static/css/all.min.css",rel="stylesheet"),
        html.Link(href="./static/stylesheet-oil-and-gas.css",rel="stylesheet"),
        html.Link(href="./static/Dosis.css", rel="stylesheet"),
        html.Link(href="./static/OpenSan.css", rel="stylesheet"),
        html.Link(href="./static/Ubuntu.css", rel="stylesheet"),
        html.Link(href="./static/dash_crm.css", rel="stylesheet"),
        # header
        html.Div([

            html.Span("Smart Signage", className='app-title'),


            
            html.Div(
                html.Img(src='./static/logo.png',height="80%")
                ,style={"float":"right","height":"80%","margin":"1% 1%"})
            ],
            className="row header"
            ),

        # Filters
        html.Div(id='filter_content',className="row",style={"margin": "2% 3%"}),


        # Data Caches
        html.Div(
               id="effectiveness_df",
               style={"display": "none"},
        ),
        html.Div(
               id="recommendation_df",
               style={"display": "none"},
        ),
         html.Div(
               id="live_person_df",
               style={"display": "none"},
        ),
        html.Div(
               id="store_df",
               style={"display": "none"},
        ),


        html.Div(
               id="signage_df",
               style={"display": "none"},
        ),

        html.Div(
               id="person_signage_list_df",
               style={"display": "none"},
        ),
        html.Div(
               id="selected_enterprise_df",
               style={"display": "none"},
        ),



        #tabs
        html.Div([

        html.Div([
                        dcc.Tabs(
                            id="tabs",
                            value="setup_tab",
                            children=[

                                dcc.Tab(label="Setup", value="setup_tab",style=tab_style, selected_style=tab_selected_style),
                                dcc.Tab(label="Explore", value="live_tab",style=tab_style, selected_style=tab_selected_style),
                                dcc.Tab(label="Insights", value="audience_tab",style=tab_style, selected_style=tab_selected_style),
                                dcc.Tab(label="Demographics Effectiveness", value="audience_demo_effect_tab",style=tab_style, selected_style=tab_selected_style),
                                dcc.Tab(label="Recommendation", value="recommendation_tab",style=tab_style, selected_style=tab_selected_style),
                                dcc.Tab(label="Compare Signages", value="snapshot_tab",style=tab_style, selected_style=tab_selected_style),

                            ]
                        ,style=tabs_styles),
                ],className="twelve columns",),
            
            ],
            className="row",style={"margin": "2% 3%"}
        ),
  
        html.Div(
                signage_manager.enterprise().to_json(orient='split'),
                id ="all_enterprise_df",
                style={"display":"none"},
            ),

        html.Div(
                signage_manager.get_init_push().to_json(orient='split'),
               id="snapshot_df",
                style={"display": "none"},
        ),
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),

        html.Span("Copyright 2019 JCI All rights reserved", className='footer-title')

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
    elif tab == "audience_tab":
        return overall.layout
    elif tab == "audience_demo_effect_tab":
        logger.info(tab)
        return demographics.layout
    elif tab == "recommendation_tab":
        return recommendations.layout
    elif tab == "setup_tab":
        return filter.layout






if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)

