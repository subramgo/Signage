import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from app import app, server, signage_manager
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
enterprise_drops = signage_manager.get_enterprise()


layout =[




        html.Div([

          html.Div([

        html.Div([html.P("Enterprise")]),

        html.Div([
             dcc.Dropdown(
            id='enterprise-dropdown',
            options=enterprise_drops[0],
            #value=enterprise_drops[1],
            #placeholder="Select Enterprise",
            clearable=False,

            ), 

            html.Button('Switch', id='switch-button'),
        ],
        ),
      ],className="three columns",
      ),

		             
		          html.Div([
			             html.Div([html.P("Store")]),
		              
		              html.Div([

			              dcc.Dropdown(
			                    id='store-dropdown',
			  		            #placeholder="Select Store",
    							clearable=True,


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
		                    #placeholder="Select Signage",
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




####################### update data ########################


@app.callback(
    Output("recommendation_df", "children"),
    [Input("signage_df", "children")]
)
def live_recommendation_df_callback(signage_df):


    df = pd.read_json(signage_df, orient='split')
    signage_id = df['signage_id'].iloc[0]

    df = signage_manager.get_recommendation(signage_id)

    
    if df.empty == True:
        return pd.DataFrame({})

    return df.to_json(date_format='iso', orient='split')

@app.callback(
    Output("effectiveness_df", "children"),
    [Input("signage_df", "children")]
)
def live_effectivness_df_callback(signage_df):


    df = pd.read_json(signage_df, orient='split')
    signage_id = df['signage_id'].values[0]
    signage_id = str(signage_id)


    df = signage_manager.overall_effectiveness(signage_id)
    
    if df.empty == True:
        return pd.DataFrame({})

    return df.to_json(date_format='iso', orient='split')


@app.callback(
    Output("live_person_df", "children"),
    [Input("signage_df", "children")]
)
def live_person_df_callback(signage_df):


    df = pd.read_json(signage_df, orient='split')

    signage_id = df['signage_id'].values[0]
    signage_id = str(signage_id)


    df = signage_manager.live_person(signage_id)

    
    if df.empty == True:
        return pd.DataFrame({})

    return df.to_json(date_format='iso', orient='split')

##################################### Update Signage #########################

@app.callback(
    Output("person_signage_list_df", "children"),
    [Input("store-dropdown", "value")]
)
def live_person_all_df_callback(store_id):

    df = signage_manager.person_all_signage(store_id)
    return df.to_json(date_format='iso', orient='split')


@app.callback(
    Output('signage_df', 'children'),
    [Input('store-dropdown', 'value')])
def load_signage_df_value(store_id):
    value = signage_manager.get_signage(store_id)[1]
    print
    df = pd.DataFrame({'signage_id': [value]})
    return df.to_json(date_format='iso', orient='split') 

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

############# Update Store #######################
@app.callback(
    Output('store_df', 'children'),
    [Input('store-dropdown', 'value')])
def load_store_df_value(store_id):
	df = pd.DataFrame({'store_id': [store_id]})
	
	return df.to_json(date_format='iso', orient='split') 

@app.callback(
    Output('store-address', 'children'),
    [Input('store-dropdown', 'value')])
def load_stores_address(store_id):
    options = signage_manager.store(store_id)
    if options.empty == True:
    	return "NA"
    return options['address'] + ',' + options['city'] + ',' + options['state']


@app.callback(
    Output('store-dropdown', 'options'),
    [Input('selected_enterprise_df', 'children')])
def load_stores_option(selected_enterprise_df):
	df = pd.read_json(selected_enterprise_df, orient='split')
	enterprise_id = df['enterprise_id'].iloc[0]
	options = signage_manager.get_stores(enterprise_id)[0]
	return options

@app.callback(
    Output('store-dropdown', 'value'),
    [Input('selected_enterprise_df', 'children')])
def load_stores_value(selected_enterprise_df):
	df = pd.read_json(selected_enterprise_df, orient='split')
	enterprise_id = df['enterprise_id'].iloc[0]
	value = signage_manager.get_stores(enterprise_id)[1]
	return value 


# Step 1 - Store the selected enterprise id
@app.callback(
    Output('selected_enterprise_df', 'children'),
    [Input('enterprise-dropdown', 'value')])
def load_enterprise_df_value(enterprise_id):

    
    df = pd.DataFrame({'enterprise_id': [enterprise_id]})
    return df.to_json(date_format='iso', orient='split') 

"""



"""
