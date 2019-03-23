import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from app import app, server, signage_manager
import dash_table


rules_df = pd.DataFrame({})


@app.callback(
    Output("recommendation_table", "data"),
    [Input("recommendation_df", "children"),Input("demo_trigger_df","children")]
)
def get_recommendation_data(recommendation_df,_):
    
    rules_df = pd.read_json(recommendation_df, orient='split')
    return rules_df.to_dict("rows")

@app.callback(
    Output("recommendation_table", "columns"),
    [Input("recommendation_df", "children"),Input("demo_trigger_df","children")]
)
def get_recommendation_columns(recommendation_df,_):
    rules_df = pd.read_json(recommendation_df, orient='split')
	
    return [{"name": i, "id": i} for i in rules_df.columns]

layout =[

        html.Div([

        	      dash_table.DataTable(
					    id='recommendation_table',
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