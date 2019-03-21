import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from app import app, server, signage_manager

enterprise_drops = signage_manager.get_enterprise()


layout =[



        html.Div([

        	      html.Div([

        			 html.Div([html.P("Enterprise")]),

		              html.Div([
		                     dcc.Dropdown(
		                    id='enterprise-dropdown',
		                    options=enterprise_drops[0],
		                    value=enterprise_drops[1],
		                    placeholder="Select Enterprise",
    clearable=False,

		                    ), 
		                ],
		                ),
		              ],className="three columns",
		              ),

		             
		          html.Div([
			             html.Div([html.P("Store")]),
		              
		              html.Div([

			              dcc.Dropdown(
			                    id='store-dropdown',
			  		            placeholder="Select Store",
    clearable=False,


			                    ), 
			                ],
		                ),


		             ],className="three columns"


		             ),

        	html.Div([

        			 html.Div([html.P("Signage")]),

		              html.Div([
		                     dcc.Dropdown(
		                    id='signage-dropdown',
		                    placeholder="Select Signage",
    clearable=False,
		           

		                    ), 
		                ],

		                ),
		             ],className="three columns",

                    ),
		             
		            
		    html.Div([

        			 html.Div([html.P("Address")]),
						html.H5(id="store-address"),
		                ],
		             className="three columns",


		           ),

		             
		             

		             


            ],
            ),
]

@app.callback(
    Output('signage-dropdown', 'options'),
    [Input('store-dropdown', 'value')])
def load_signage_option(store_id):
    options = signage_manager.get_signage(store_id)[0]
    return options

@app.callback(
    Output('signage-dropdown', 'value'),
    [Input('store-dropdown', 'value')])
def load_signage_value(store_id):
    value = signage_manager.get_signage(store_id)[1]
    return value 


@app.callback(
    Output('store-address', 'children'),
    [Input('store-dropdown', 'value')])
def load_stores_address(store_id):
    options = signage_manager.store(store_id)
    return options['address'] + ',' + options['city'] + ',' + options['state']

@app.callback(
    Output('store-dropdown', 'options'),
    [Input('enterprise-dropdown', 'value')])
def load_stores_option(enterprise_id):
    options = signage_manager.get_stores(enterprise_id)[0]
    return options

@app.callback(
    Output('store-dropdown', 'value'),
    [Input('enterprise-dropdown', 'value')])
def load_stores_value(enterprise_id):
	value = signage_manager.get_stores(enterprise_id)[1]
	return value 