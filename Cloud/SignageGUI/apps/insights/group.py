import dash_core_components as dcc
import dash_html_components as html

from app import signage_manager, app


get_locations = signage_manager.get_locations


layout = [

    html.Div([
	#charts row div 
        html.Div(
            [
                html.Div(
                    [
                                dcc.Dropdown(
                                id='grp1_location-dropdown',
                                options=get_locations()[0],
                                value=get_locations()[1],
                                )
                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),
                
                html.Div([html.P("")]),
                
                html.Div(
                    [
						dcc.Checklist(
						    options=[
						        {'label': 'Age', 'value': 'age'},
						        {'label': 'Gender', 'value': 'gender'},
						        {'label': 'Time of day', 'value': 'tod'},
						        {'label': 'Day of week', 'value':'dow'}
						    ],
						    values=['age', 'gender','tod','dow']
						),
                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),
                

            ],
            className="four columns",
    	),
    	],

         className="row",
        style={"marginTop": "5px", "max height": "600px"},
    ),
]

