import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import numpy as np
from app import signage_manager, app
from dash.dependencies import Input, Output
import dash_table
import pandas as pd

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
enterprise_drops = signage_manager.get_enterprise()





@app.callback(
    Output("demograhics_effectiveness", "figure"),
    [Input("effectiveness_df", "children"),Input("demo_trigger_df","children")]
)
def demo_effectiveness(effect_df, _):
    logger.info("demo effectiveness")
    df = pd.read_json(effect_df, orient='split')

    return get_demo_effect(df)

def get_demo_effect(df):
	
	#df = signage_manager.overall_effectiveness(signage_id)

	
	scales = ['<b>Male</b>', '<b>Female</b>',
	          '<b>Adult</b>', '<b>Teen</b>', '<b>Senior</b>']
	

	scale1 = ['Not <br> Effective ','Very Low <br> Effective ', 'Low <br> Effective ',
	           'Neutral ',
	          'Moderately <br> Effective ', 'Highly <br> Effective ','Peak <br> Effective ',
	          ]
	scale2 = ['Not <br> Effective ','Very Low <br> Effective ', 'Low <br> Effective ',
	           'Neutral ',
	          'Moderately <br> Effective ', 'Highly <br> Effective ','Peak <br> Effective ',
	          ]
	scale3 = ['Not <br> Effective ','Very Low <br> Effective ', 'Low <br> Effective ',
	           'Neutral ',
	          'Moderately <br> Effective ', 'Highly <br> Effective ','Peak <br> Effective ',
	          ]
	scale4 = ['Not <br> Effective ','Very Low <br> Effective ', 'Low <br> Effective ',
	           'Neutral ',
	          'Moderately <br> Effective ', 'Highly <br> Effective ','Peak <br> Effective ',
	          ]
	scale5 = ['Not <br> Effective ','Very Low <br> Effective ', 'Low <br> Effective ',
	           'Neutral ',
	          'Moderately <br> Effective ', 'Highly <br> Effective ','Peak <br> Effective '
	          ]


	scale_labels = [scale1, scale2, scale3, scale4, scale5]
	fill_colors  = ['#1C4E80', '#0088cc','#0091D5','#f67519','#6ead3a']

	# Add Scale Titles to the Plot
	traces = []
	for i in range(len(scales)):
	    traces.append(go.Scatter(
	        x=[0.6], # Pad the title - a longer scale title would need a higher value 
	        y=[6.30],
	        text=scales[i],
	        mode='text',
	        hoverinfo='none',
	        showlegend=False,
	        xaxis='x'+str(i+1),
	        yaxis='y'+str(i+1),
	    ))
	
	# Create Scales
	## Since we have 5 lables, the scale will range from 0-5
	shapes = []
	for i in range(len(scales)):
	    shapes.append({'type': 'rect',
	                   'x0': .02, 'x1': 1.02,
	                   'y0': 0, 'y1': 6,
	                   'xref':'x'+str(i+1), 'yref':'y'+str(i+1), 'fillcolor': fill_colors[i],'opacity': 0.8})
	
	x_domains = [[0, .2], [.2, .4], [.4, .6], [.6, .8],[.8, 1]] # Split for 5 scales

	# Define X-Axes
	xaxes = []
	for i in range(len(scales)):
	    xaxes.append({'domain': x_domains[i], 'range':[0, 3.5],
	                  'showgrid': False, 'showline': False,
	                  'zeroline': False, 'showticklabels': False})


	# Define Y-Axes (and set scale labels)
	## ticklen is used to create the segments of the scale,
	## for more information see: https://plot.ly/python/reference/#layout-yaxis-ticklen
	yaxes = []
	chart_width = 1000
	for i in range(len(scales)):
	    yaxes.append({'anchor':'x'+str(i+1), 'range':[-.5,7.0],
	                  'showgrid': False, 'showline': False, 'zeroline': False,
	                  'ticks':'inside', 'ticklen': chart_width/20,
	                  'ticktext':scale_labels[i], 'tickvals':[0., 1., 2., 3., 4., 5., 6.]
	                 })


	# Put all elements of the layout together
	layout = {'shapes': shapes,
	          'xaxis1': xaxes[0],
	          'xaxis2': xaxes[1],
	          'xaxis3': xaxes[2],
	          'xaxis4': xaxes[3],
	          'xaxis5': xaxes[4],

	          'yaxis1': yaxes[0],
	          'yaxis2': yaxes[1],
	          'yaxis3': yaxes[2],
	          'yaxis4': yaxes[3],
	          'yaxis5': yaxes[4],

	          'autosize': False,
	          'width': chart_width,
	          'height': 600
	}

	male_rating = 0
	female_rating = 0
	teen_rating = 0
	adult_rating = 0
	senior_rating = 0

	male_rating = df[df.gender == 'male']['normalized_engagement'].mean() * 10
	female_rating = df[df.gender == 'female']['normalized_engagement'].mean() * 10

	teen_rating = df[df.age == 'teen']['normalized_engagement'].mean() * 10
	adult_rating = df[df.age == 'adult']['normalized_engagement'].mean() * 10
	senior_rating = df[df.age == 'senior']['normalized_engagement'].mean() * 10


	ratings = [male_rating, female_rating, teen_rating, adult_rating, senior_rating]

	for i in range(len(ratings)):
	    traces.append(go.Scatter(
	            x=[0.5], y=[ratings[i]],
	            xaxis='x'+str(i+1), yaxis='y'+str(i+1),
	            mode='markers', marker={'size': 16, 'color': 'black'},
	            text=str(ratings[i]), hoverinfo='text', showlegend=False
	    ))

	return {'data': traces,'layout': layout}


############################### Layout Begin ##########################################

layout = [

                    html.Div(
               id="demo_trigger_df",
               style={"display": "none"},
        ),

html.Div([html.P("")]),


html.Div([
	#charts row div 
        html.Div(
            [



                html.Div(
                    [
                   dcc.Graph(
                        id = "demograhics_effectiveness",
                        style={"height": "100%", "width": "50%","margin":5},
                        config=dict(displayModeBar=False),
                    ),
                    ],

                    ),

                
            ],
    	),
        ],
       # className="row",
        style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

        )
    
]
