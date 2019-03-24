import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import numpy as np
from app import app, app_state
from dash.dependencies import Input, Output
import pandas as pd


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def get_total_score():

	df = app_state.effectiveness_df

	if df is None or df.empty == True :
	    return {'data':[],'layout':[]}


	x1 = np.round(df['normalized_engagement'].mean() * 100,2)

	return "Selected signage has an overall effectiveness score of {}".format(x1)






def get_overall_time_alive():

	#df = signage_manager.overall_effectiveness(signage_id)

	df = app_state.effectiveness_df

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




def get_overall_engagement():

	#df = signage_manager.overall_effectiveness(signage_id)

	df = app_state.effectiveness_df

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




def get_engagement_score_box_chart():
	#df = signage_manager.overall_effectiveness(signage_id)
	df = app_state.effectiveness_df

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





############################### Layout Begin ##########################################


layout = [





	html.Div([html.P("")]),




	html.Div([
        
 
	     
			html.H4(get_total_score(),id="total_score", style={"text-align":"center"}),


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
                        figure = get_overall_time_alive(),
                    ),
                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),
                
            ],
            className="four columns",
    	),
        html.Div(
               id="trigger_df",
               style={"display": "none"},
        ),
        html.Div(
            [
                html.Div(
                    [
                   dcc.Graph(
                        id = "overall_engagement",
                        style={"height": "100%", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                        figure = get_overall_engagement(),

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
                        figure = get_engagement_score_box_chart()
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