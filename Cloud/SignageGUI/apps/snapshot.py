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

	df = signage_manager.demographics()

	if df.empty == True:
		return {'data':[],'layout':[]}

	df = df[['location','age_list']]

	locations = df['location'].unique()

	data = []
	for location in locations:
		age_list = df[df['location'] == location]['age_list'].tolist()
		age_bukts = [age_bucket for age_bucket in itertools.chain.from_iterable(age_list)]
		counter = collections.Counter(age_bukts)

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
	)

	return {"data":data,"layout":layout}



########################### Demographics chart ############################

def get_demographics_chart():

	df = signage_manager.demographics()


	if df.empty == True:
		return {"data":[],"layout":[]}

	df = df[['location','male_count','female_count']]

	locations = df['location'].unique()

	male_count = []
	female_count = []

	for location in locations:
		male_count.append(sum(df[df['location'] == location]['male_count'].tolist()))
		female_count.append(sum(df[df['location'] == location]['female_count'].tolist()))

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
	)

	return {"data":data,"layout":layout}



######################### Dwell time chart ##############################

def get_dwelltime_chart():

	df = signage_manager.activity()
	df = df[['location','time_alive']]

	if df.empty == True:
		return {"data":[],"layout":[]}

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
	)

	return {"data":data,"layout":layout}

###################### Impressions chart ############################

def get_impressions_chart():


	df = signage_manager.faces()

	if df.empty == True:
		return {"data":[],"layout":[]}

	df = df[['location','no_faces']]
	df = df[df['no_faces'] != 0]

	locations = df['location'].unique()
	bar_data = []
	for location in locations:
		bar_data.append( sum(df[df['location'] == location]['no_faces'].tolist()) )

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
	)

	return {"data":data,"layout":layout}


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
	#charts row div 
    html.Div(
        [
            html.Div(
                [
                    html.P("Total Impressions"),
                    dcc.Graph(
                        id = "impressions_chart",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                        figure =get_impressions_chart()
                    ),
                ],
                className="six columns chart_div",
                ),
            html.Div(
                [
                    html.P("Average Dwell time"),
                    dcc.Graph(
                        id = "dwelltime_chart",
                        style = {"height": "90%", "width": "98%"},
                        config = dict(displayModeBar=False),
                        figure = get_dwelltime_chart()
                    ),
                ],
                className="six columns chart_div",
                ),
            

        ],
        className="row",
        style={"marginTop": "5px"}
	),
	#charts row div 
    html.Div(
        [
            html.Div(
                [
                    html.P("Demographics"),
                    dcc.Graph(
                        id = "demograpics_chart",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                        figure =get_demographics_chart()
                    ),
                ],
                className="six columns chart_div",
                ),
            html.Div(
                [
                    html.P("Engagement"),
                    dcc.Graph(
                        id = "engagement_chart",
                        style = {"height": "90%", "width": "98%"},
                        config = dict(displayModeBar=False),
                        figure = get_age_bar(),
                    ),
                ],
                className="six columns chart_div",
                ),
            

        ],
        className="row",
        style={"marginTop": "5px"}
	),


 ]










