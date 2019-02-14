#!/usr/bin/env python
"""Provides html divs, data and graphs for live view.


"""
import dash_html_components as html
from app import signage_manager, app
from dash.dependencies import Input, Output, State

import numpy as np
import dash_core_components as dcc
from plotly import graph_objs as go
import pandas as pd
import itertools
import collections
import ast
import plotly.figure_factory as ff

__author__ = "Gopi Subramanian"
__maintainer__ = "Gopi Subramanian"
__status__ = "Proof of concept"

def get_locations():
    """
    Returns list of location for drop down box
    """
    faces = signage_manager.faces()
    if faces.empty == True:
        return ({'label': "NA", 'value': "NA"},"N/A")

    locations = faces['location'].unique()

    options_ = []

    for location in locations:
        option = {'label': location, 'value': location}
        options_.append(option)

    return (options_, location)


#################### First row header ################################


@app.callback(
    Output("live_faces_count", "children"),
    [Input("location-dropdown", "value")]
)
def live_count_callback(location):
    return get_live_count(location)

def get_live_count(location):
    """
    Total impressions count
    """

    df = signage_manager.live_faces(location)
    if df.empty == True:
        return "\n Total Faces NA"
    
    count = df['no_faces'].sum()
    return "\nTotal Faces " + str(count)



@app.callback(
    Output("live_male_count", "children"),
    [Input("location-dropdown", "value")]
)
def live_male_count_callback(location):
    return get_male_count(location)

def get_male_count(location):

    demographics = signage_manager.live_demograhics(location)
    
    if demographics.empty == True:
        return "\nMales NA"


    count = demographics['male_count'].sum()
    return "\nMales " + str(count)




@app.callback(
    Output("live_female_count", "children"),
    [Input("location-dropdown", "value")]
)
def live_female_count_callback(location):
    return get_female_count(location)

def get_female_count(location):

    demographics = signage_manager.live_demograhics(location)

    if demographics.empty == True:
        return "\nFemales NA"

    count = demographics['female_count'].sum()
    return "\nFemales " + str(count)


@app.callback(
    Output("live_activity", "children"),
    [Input("location-dropdown", "value")]
)
def live_activity_callback(location):
    return get_activity(location)

def get_activity(location):
    df = signage_manager.live_activity(location)

    if df.empty == True:
        return "Dwell time NA"
    else:
        return "Dwell time " + str(np.round(df['time_alive'].mean()))


@app.callback(
    Output("live_engagement", "children"),
    [Input("location-dropdown", "value")]
)
def live_engagement_callback(location):
    return get_engagement(location)

def get_engagement(location):
   
    faces = signage_manager.live_faces(location)

    if faces.empty == True:
        return "Engagement Range NA"

    faces_ = np.array(faces['distances'].tolist())
    mean_values = []
    for row in faces_:
        mean_values.append(np.array(row).mean())
    
    engagement = np.array(mean_values).mean()


    return "Engagement Range " + str(np.round(engagement,2) )





############################# Dwell Chart ######################

@app.callback(
    Output("live_dwell_chart", "figure"),
    [Input("location-dropdown", "value")]
)
def live_dwell_callback(location):
    return get_live_dwell_chart(location)

def get_live_dwell_chart(location):
    df = signage_manager.live_activity(location)
    if df.empty == True:
        return {'data':[],'layout':[]}

    hist_data = df['time_alive'].tolist()
    fig = ff.create_distplot([hist_data], ["Dwell time"],bin_size=[1, 10, 20, 30])

    fig['layout'].update(title='Dwell time distribution')
    return fig




############################### Live age chart ###################

@app.callback(
    Output("live_age_chart", "figure"),
    [Input("location-dropdown", "value")]
)
def live_age_callback(location):
    return get_live_age_chart(location)


def get_live_age_chart(location):

    df = signage_manager.live_demograhics(location)

    if df.empty == True:
        return {"data":[],"layout":[]}

    unique_age_buckets = []

    age_list = df['age_list'].tolist()
    for age in age_list:
        content = ast.literal_eval(age)

        # Single or multiple tuples ?
        if type(content[0]) == int:
            unique_age_buckets.append(content)
        elif type(content[0]) == tuple:
            for c in content:
                unique_age_buckets.append(c) 

    counter_ = collections.Counter(unique_age_buckets)

    x_labels = []
    for ab in list(counter_.keys()):
        x_labels.append(str(ab))

    trace1 = go.Bar(
        x=x_labels,
        y=list(counter_.values()),
    )


    data = [trace1]


    layout = go.Layout(
        xaxis=dict(showgrid=True),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title="Age distribution",
    )

    return {"data":data,"layout":layout}





############################### Live Gender chart ###################

@app.callback(
    Output("live_gender_chart", "figure"),
    [Input("location-dropdown", "value")]
)
def live_gender_callback(location):
    return get_live_gender_chart(location)


def get_live_gender_chart(location):
    df = signage_manager.live_demograhics(location)


    if df.empty == True:
        return {"data":[],"layout":[]}

    df = df[['location','male_count','female_count']]


    male_count = []
    female_count = []

    male_count   = sum(df['male_count'].tolist())
    female_count = sum(df['female_count'].tolist())

    trace1 = go.Bar(
        x=["Male","Female"],
        y=[male_count,female_count],
    )


    data = [trace1]

    layout = go.Layout(
        xaxis=dict(showgrid=False),
        #margin=dict(l=35, r=25, b=25, t=5, pad=2),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title="Gender distribution",
    )

    return {"data":data,"layout":layout}

############################### Live Impressions chart ###################

@app.callback(
    Output("live_impressions_chart", "figure"),
    [Input("location-dropdown", "value")]
)
def live_impressions_callback(location):
    return get_live_impressions_chart(location)

def get_live_impressions_chart(location):

    df = signage_manager.live_faces(location)

    if df.empty == True:
        return {"data":[],"layout":[]}

    df['date_created'] = pd.to_datetime(df['date_created'],unit='s')

    times = pd.DatetimeIndex(df.date_created)
    df = df.groupby([times.hour]).no_faces.sum()

    df = df.reset_index()

    data = [go.Scatter( x=df['date_created'], y=df['no_faces'] )]

    layout = go.Layout(
        title="Total Impressions",
        xaxis=dict(showgrid=False,title="Hours"),
        yaxis=dict(title="Impressions"),
        #margin=dict(l=35, r=25, b=25, t=5, pad=2),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data":data,"layout":layout}


###################### Live Engagement Chart ########################

@app.callback(
    Output("live_engagement_chart", "figure"),
    [Input("location-dropdown", "value")]
)
def live_engagement_callback(location):
    return get_live_engagement_chart(location)



def get_live_engagement_chart(location):

    df = signage_manager.live_faces(location)

    if df.empty == True:
        return {'data':[],'layout':[]}

    distances = np.around([distance for distance 
        in itertools.chain.from_iterable(df['distances'].tolist())], decimals=2)

    count, y_values = np.histogram(distances, bins = 5, range=(1.0, max(distances)))


    data_frame = pd.DataFrame()
    x_values = []
    y_vals   = []


    for i in range(len(count)):
        if count[i] > 0:
            x_values.extend(np.random.randint(low=1, high=25, size=count[i]))
            y_vals.extend(np.repeat( ( (y_values[i] + y_values[i+1] )/2*1.0) 
                + (np.random.random()), count[i]))

    data_frame['x_vals'] = x_values
    data_frame['y_vals'] = y_vals


    trace0 = go.Scatter(
        x = data_frame['x_vals'],
        y = data_frame['y_vals'],
        name = 'Above',
        mode = 'markers',
        marker = dict(
            size = 5,
            color = '#EA6A47',
            line = dict(
                width = 1,
                color = '#EA6A47'
            )
        )
    )



    data = [trace0]

    layout = dict(
                  title ="Engagement Range",
                  yaxis = dict(zeroline = False, title="Feet",xticks=None, range=(0,6)),
                  xaxis = dict(zeroline = False, showgrid=False, title="Screen", tickvals=[])
                 )

    return dict(data=data, layout=layout)

###############################################################################################

layout = [

       html.P(
        '',
        className="twelve columns indicator_text",

    ),

    # drop down

    html.Div([
                dcc.Dropdown(
                        id='location-dropdown',
                        options=get_locations()[0],
                        value=get_locations()[1],

                    ),
                ],
                className="row",
                style={"marginTop": "15px", "max height": "200px"},

                ),

    #indicators row
    html.Div(
        [


            html.Div(
                html.P(
                    id="live_faces_count",
                ),
                className="fa fa-user fa-2x fa-border icon-blue badge badge-blue two columns",


                ),

             html.Div(
                html.P(
                    id="live_male_count",
                ),
                className="fa fa-male fa-2x fa-border icon-grey badge two columns",


                ),

            html.Div(
                html.P(
                    id="live_female_count",
                ),
                className="fa fa-female fa-2x fa-border icon-blue badge badge-blue two columns",


                ),



            html.Div(
                html.P(
                    id="live_activity",
                ),
                className="fa fa-cogs fa-2x fa-border icon-grey badge two columns",


                ),


            html.Div(
                html.P(
                 id="live_engagement",
                ),
                className="fa fa-eye fa-2x fa-border icon-blue badge badge-blue two columns",


                ),


            ],
                        className="row",
                        style={"marginTop": "15px", "max height": "200px"},
                	),

    # Charts
    html.Div(
        [
            
            html.Div(
                [
                    html.P("     "),
                    dcc.Graph(
                        id = "live_engagement_chart",
                        style = {"height": "505", "width": "98%","margin":5},
                        config = dict(displayModeBar=False),
                    ),
                ],
                style={'border':'1px solid', 'border-radius': 10, 'backgroundColor':'#FFFFFF'},

                className="four columns",


                ),


            html.Div(
                [
                    html.P(" "),
                    dcc.Graph(
                        id = "live_impressions_chart",
                        style={"height": "250", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),

                    html.P("        "),
                    dcc.Graph(
                        id = "live_gender_chart",
                        style={"height": "250", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),


                ],
                style={'border':'1px solid', 'border-radius': 10, 'backgroundColor':'#FFFFFF'},

                className = "four columns",



            ),

                html.Div(
                [
                    html.P(" "),
                    dcc.Graph(
                        id = "live_dwell_chart",
                        style={"height": "250", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),

                    html.P("        "),
                    dcc.Graph(
                        id = "live_age_chart",
                        style={"height": "250", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),


                ],
                style={'border':'1px solid', 'border-radius': 10, 'backgroundColor':'#FFFFFF'},

                className = "four columns",



            ),

        ],
        className="row",
        style={"marginTop": "5px", "max height": "600px"},
    ),

]