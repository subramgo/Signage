import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from app import app, server, app_state
import dash_table





def get_recommendation_data():
    
    rules_df = app_state.recommendation_df
    return rules_df.to_dict("rows")


def get_recommendation_columns():
    rules_df = app_state.recommendation_df
	
    return [{"name": i, "id": i} for i in rules_df.columns]

layout =[

        html.Div([

        	      dash_table.DataTable(
					    id='recommendation_table',
					    data = get_recommendation_data(),
					    columns = get_recommendation_columns(),
    style_cell={'textAlign': 'center'},
    style_cell_conditional=[
        {
            'if': {'column_id': 'Recommendation'},
            'textAlign': 'center'
        }
    ]
					),


            ],
            ),
]