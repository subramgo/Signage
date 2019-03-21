import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import numpy as np
from app import signage_manager, app
from dash.dependencies import Input, Output




@app.callback(
    Output("total_score", "children"),
    [Input("signage-dropdown", "value")]
)
def get_total_score(signage_id):
	df = signage_manager.overall_effectiveness(signage_id)

	sign_details = signage_manager.signage_details(signage_id)
	print(sign_details)
	store_details = signage_manager.store(int(sign_details['store_id']))

	if df.empty == True :
	    return {'data':[],'layout':[]}

	print(store_details)

	x1 = np.round(df['normalized_engagement'].mean() * 100,2)

	return "Signage {} at {} in {} has an overall effectiveness score of {}".format(sign_details['id'], sign_details['zone'], store_details['store_name'],x1)


@app.callback(
    Output("overall_time_alive", "figure"),
    [Input("signage-dropdown", "value")]
)
def effect_timealive(signage_id):
    return get_overall_time_alive(signage_id)

def get_overall_time_alive(signage_id):

	df = signage_manager.overall_effectiveness(signage_id)

	x1 = df['time_alive']
	y1 = df['engagement_timealive']

	trace0 = go.Scatter(
	    x = x1,
	    y = y1,
	    mode = 'markers',
	    name = 'Time alive'
	)

	data = [trace0]

	layout = go.Layout(
	              yaxis = dict(zeroline = False, title='Score'),
	              xaxis = dict(zeroline = False, title='Dwell Time in seconds'),
	    title="Dwell Time Effectiveness Score"
	)

	return {"data":data, "layout":layout}


@app.callback(
    Output("overall_engagement", "figure"),
    [Input("signage-dropdown", "value")]
)
def effect_engagement(signage_id):
    return get_overall_engagement(signage_id)

def get_overall_engagement(signage_id):

	df = signage_manager.overall_effectiveness(signage_id)

	x1 = df['engagement_range']
	y1 = df['engagement_distance']


	trace0 = go.Scatter(
	    x = x1,
	    y = y1,
	    mode = 'markers',
	    name = 'Time alive'
	)

	data = [trace0]

	layout = go.Layout(
	              yaxis = dict(zeroline = False, title='Score'),
	              xaxis = dict(zeroline = False, title='Engagement distance in Ft'),
	    title="Engagement Effectiveness Score"
	)

	return {"data":data, "layout":layout}


@app.callback(
    Output("engagement_score", "figure"),
    [Input("signage-dropdown", "value")]
)
def engagement_score_box(signage_id):
    return get_engagement_score_box_chart(signage_id)

def get_engagement_score_box_chart(signage_id):
	df = signage_manager.overall_effectiveness(signage_id)

	if df.empty == True :
	    return {'data':[],'layout':[]}

	x1 = np.array(df['normalized_engagement'], dtype=np.float32)


	trace = go.Box(
	    y=x1,
	    name="Effectiveness",
	    )



	data = [trace]

	layout = go.Layout(
	    title="Overall Effectivness Score",
		xaxis=dict(
	    zeroline=True
		),
		yaxis=dict(title='Score')
	)

	return dict(data=data, layout=layout)


layout = [


html.Div([html.P("")]),


html.Div([

     
		html.H4(id="total_score", style={"text-align":"center"}),


	],

        #className="row",
        style={'border':'1px solid', 'border-radius': 8, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},


	),

html.Div([html.P("")]),

 html.Div([
	#charts row div 
        html.Div(
            [
                html.Div(
                    [
                   dcc.Graph(
                        id = "overall_time_alive",
                        style={"height": "100%", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),
                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),
                
            ],
            className="four columns",
    	),

        html.Div(
            [
                html.Div(
                    [
                   dcc.Graph(
                        id = "overall_engagement",
                        style={"height": "100%", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),
                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),
                
            ],
            className="four columns",
    	),

        html.Div(
            [
                html.Div(
                    [
                   dcc.Graph(
                        id = "engagement_score",
                        style={"height": "100%", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),
                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),
                
            ],
            className="four columns",
    	),


    	],

         #className="row",
        style={"marginTop": "5px", "max height": "600px"},
    ),
]