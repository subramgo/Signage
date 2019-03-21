import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from app import app, server, signage_manager
import dash_table

@app.callback(
    Output("recommendation_table", "data"),
    [Input("signage-dropdown", "value")]
)
def get_recommendation(signage_id):
	rules_df = signage_manager.get_recommendation(signage_id)
	
	return rules_df

layout =[



        html.Div([

        	      dash_table.DataTable(
					    id='recommendation_table',
					)


            ],
            ),
]