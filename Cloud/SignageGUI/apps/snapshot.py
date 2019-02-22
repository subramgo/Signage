#!/usr/bin/env 
"""Provides html divs, data and graphs for snapshot view.


"""

import dash_html_components as html
import dash_core_components as dcc
from app import indicator,indicator_alt,app,signage_manager
from dash.dependencies import Input, Output, State
import pandas as pd 
import numpy as np
import plotly
from plotly import graph_objs as go
import plotly.figure_factory as ff
import collections
import itertools


###################### First row header call backs #######################

@app.callback(
    Output("avg_dwell_time", "children"),
    [Input("snapshot_df", "children")]
)
def dwell_time_callback(df_json):
	df = pd.read_json(df_json, orient="split")
	avg_dwell_time = df['Avg Dwell time']
	return str(int(avg_dwell_time)) + " seconds"

@app.callback(
    Output("engagement_range", "children"),
    [Input("snapshot_df", "children")]
)
def engagement_callback(df_json):
	df = pd.read_json(df_json, orient="split")
	engagement_range = df['Engagement Range']
	return str(float(np.round(engagement_range,decimals=1))) + " Feet"

@app.callback(
    Output("male_count", "children"),
    [Input("snapshot_df", "children")]
)
def male_count_callback(df_json):
	df = pd.read_json(df_json, orient="split")
	male_count = df['Male Count']
	return str(float(np.round(male_count,decimals=1)))

@app.callback(
    Output("female_count", "children"),
    [Input("snapshot_df", "children")]
)
def female_count_callback(df_json):
	df = pd.read_json(df_json, orient="split")
	female_count = df['Female Count']
	return str(float(np.round(female_count,decimals=1)))


@app.callback(
    Output("age_group", "children"),
    [Input("snapshot_df", "children")]
)
def female_count_callback(df_json):
	df = pd.read_json(df_json, orient="split")
	age_group = df['Age Group']
	return age_group

@app.callback(
    Output("total_impressions", "children"),
    [Input("snapshot_df", "children")]
)
def total_impressions_callback(df_json):
	df = pd.read_json(df_json, orient="split")
	total_impressions = df['Total Impressions']
	return total_impressions


####################### Age Chart ########################

def get_age_bar():

	df = signage_manager.person()

	if df.empty == True:
		return {'data':[],'layout':[]}

	df = df[['location','age']]

	locations = df['location'].unique()

	data = []
	for location in locations:
		age_list = df[df['location'] == location]['age'].tolist()
		counter = collections.Counter(age_list)

		trace = go.Bar(
			x = list(counter.keys()),
			y = list(counter.values()),
			name=location,

			)
		data.append(trace)


	layout = go.Layout(
	    xaxis=dict(showgrid=False),
	    #margin=dict(l=35, r=25, b=25, t=5, pad=2),
	    paper_bgcolor="white",
	    plot_bgcolor="white",
        title="Age by Location"
	)

	return {"data":data,"layout":layout}



########################### Demographics chart ############################

def get_demographics_chart():

    df = signage_manager.person()


    if df.empty == True:
    	return {"data":[],"layout":[]}

    df = df.groupby(['location','gender']).aggregate({'face_id':'nunique'}).reset_index()


    locations = df['location'].unique()

    male_count = []
    female_count = []

    for location in locations:
    	male_count.append(df[ (df['location'] == location) & (df['gender'] == 'male')]['face_id'].values[0])
    	female_count.append(df[ (df['location'] == location) & (df['gender'] == 'female')]['face_id'].values[0])

    trace1 = go.Bar(
        x=locations,
        y=male_count,
        name ='Male',
    )
    trace2 = go.Bar(
        x=locations,
        y=female_count,
        name='Female',
    )

    data = [trace1, trace2]

    layout = go.Layout(
        xaxis=dict(showgrid=False),
        #margin=dict(l=35, r=25, b=25, t=5, pad=2),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title="Gender by Location"
    )

    return {"data":data,"layout":layout}



######################### Dwell time chart ##############################

def get_dwelltime_chart():

	df = signage_manager.person()

	if df.empty == True:
		return {"data":[],"layout":[]}

	df = df[['location','time_alive']]
	locations = df['location'].unique()
	bar_data = []
	for location in locations:
		vals = df[df['location'] == location]['time_alive'].tolist()
		tot  = sum(vals)
		count = len(vals)

		bar_data.append( (tot / count * 1.0) )

	data = [go.Bar(
            x=locations,
            y=bar_data,
            text=[ '%.2f' % elem for elem in bar_data ],
                textposition = 'auto',
		    marker=dict(
		        color='#0091D5',
		        line=dict(
		            color='rgb(8,48,107)',
		            width=1.5),
		        ),
    )]

	layout = go.Layout(
	    xaxis=dict(showgrid=False),
	    #margin=dict(l=35, r=25, b=25, t=5, pad=2),
	    paper_bgcolor="white",
	    plot_bgcolor="white",
        title="Average Dwell Time by Location"
	)

	return {"data":data,"layout":layout}

###################### Impressions chart ############################

def get_impressions_chart():


	df = signage_manager.person()

	if df.empty == True:
		return {"data":[],"layout":[]}

	df = df[['location','face_id']]

	locations = df['location'].unique()
	bar_data = []
	for location in locations:
		bar_data.append( df[df['location'] == location]['face_id'].nunique() )

	data = [go.Bar(
            x=locations,
            y=bar_data,
            text=bar_data,
            textposition = 'auto',
		    marker=dict(
		        color='#1C4E80',
		        line=dict(
		            color='rgb(8,48,107)',
		            width=1.5),
		        ),
    )]

	layout = go.Layout(
	    xaxis=dict(showgrid=False),
	    #margin=dict(l=35, r=25, b=25, t=5, pad=2),
	    paper_bgcolor="white",
	    plot_bgcolor="white",
        title="Impressions by Location"
	)

	return {"data":data,"layout":layout}



############################## Engatement Chart #############################

def get_engagement_chart():
    df = signage_manager.person()

    if df.empty == True:
        return {'data':[],'layout':[]}


    locations = df['location'].unique()
    data = []

    for location in locations:

        distances = df[df['location'] == location]['engagement_range'].tolist()
        x_values = np.random.randint(low=1,high=25,size=len(distances))

        trace = go.Scatter(
            x = x_values,
            y = distances,
            name = location,
            mode = 'markers',
            marker = dict(
                size = 5,
                line = dict(
                    width = 1,
                )
            )
        )
        data.append(trace)




    layout = dict(
                  title ="Engagement Range Distribution",
                  yaxis = dict(zeroline = False, title="Feet",xticks=None, range=(0,6)),
                  xaxis = dict(zeroline = False, showgrid=False, title="Screen", tickvals=[])
                 )

    return dict(data=data, layout=layout)



############################## Engagement Box Chart #########################

def get_engagement_box_chart():
    df = signage_manager.person()

    if df.empty == True:
        return {'data':[],'layout':[]}


    locations = df['location'].unique()
    data = []

    for location in locations:

        distances = df[df['location'] == location]['engagement_range'].tolist()
        trace = go.Box(
            y=distances,
            name=location,
            )
        data.append(trace)

    layout = go.Layout(
        title="Engagement Range in Foot",
    xaxis=dict(
        zeroline=True
    ),
    boxmode='group'
    )
    
    return dict(data=data, layout=layout)




############################## HTML Layout ##################################

layout = [

       html.P(
        '',
        className="twelve columns indicator_text"
    ),

    #indicators row
    html.Div(
        [
            indicator(
                "#00cc96",
                "Total Impressions",
                "total_impressions",
            ),
            indicator_alt(
                "#119DFF",
                "Average Dwell time",
                "avg_dwell_time",
            ),
            indicator(
                "#EF553B",
                "Engagement Range",
                "engagement_range",
            ),
            indicator_alt(
                "#00cc96",
                "Male Customers",
                "male_count",
            ),
            indicator(
                "#119DFF",
                "Female Customers",
                "female_count",
            ),
            indicator_alt(
                "#119DFF",
                "Frequent Age Group",
                "age_group",
            ),
        ],
        className="row",
        style={"marginTop": "5px", "max height": "200px"},
	),

    html.Div([
	#charts row div 
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id = "impressions_chart",
                            style={"height": "100%", "width": "98%","margin":5},
                            config=dict(displayModeBar=False),
                            figure =get_impressions_chart()
                        ),
                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),
                
                html.Div([html.P("")]),
                
                html.Div(
                    [
                        dcc.Graph(
                            id = "dwelltime_chart",
                            style = {"height": "100%", "width": "98%","margin":5},
                            config = dict(displayModeBar=False),
                            figure = get_dwelltime_chart()
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
                                id = "demograpics_chart",
                                style={"height": "100%", "width": "98%","margin":5},
                                config=dict(displayModeBar=False),
                                figure =get_demographics_chart(),
                            ),
                        ],
                        style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),

                    html.Div([html.P("")]),
                    
                    html.Div(
                        [
                            dcc.Graph(
                                id = "age_chart",
                                style = {"height": "100%", "width": "98%","margin":5},
                                config = dict(displayModeBar=False),
                                figure = get_age_bar(),
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
                                id = "engagement_box_chart",
                                style={"height": "100%", "width": "98%","margin":5},
                                config=dict(displayModeBar=False),
                                figure =get_engagement_box_chart()
                            ),
                        ],
                        style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                        ),


                    html.Div([html.P("")]),

                    html.Div(
                        [
                            dcc.Graph(
                                id = "engagement_chart",
                                style={"height": "100%", "width": "98%","margin":5},
                                config=dict(displayModeBar=False),
                                figure =get_engagement_chart()
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



