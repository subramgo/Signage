#!/usr/bin/env python
"""Provides html divs, data and graphs for live view.


"""
import dash_html_components as html
from app import signage_manager, app
from app import indicator,indicator_alt
from dash.dependencies import Input, Output, State
from datetime import datetime as dt

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

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





#################### First row header ################################


@app.callback(
    Output("live_faces_count", "children"),
    [Input("live_person_df", "children")]
)
def live_count_callback(person_df):

    df = pd.read_json(person_df, orient='split')

    return get_live_count(df)

def get_live_count(df):
    """
    Total impressions count
    """

    #df = signage_manager.live_person(signage_id)
    if df.empty == True:
        return "NA"
    
    count = df['face_id'].nunique()
    return str(count)



@app.callback(
    Output("live_male_count", "children"),
    [Input("live_person_df", "children")]
)
def live_male_count_callback(person_df):

    df = pd.read_json(person_df, orient='split')

    return get_male_count(df)

def get_male_count(demographics):

    try:

        #demographics = signage_manager.live_person(signage_id)
        demographics = demographics.groupby(['gender']).aggregate({'face_id':'nunique'}).reset_index()
    except:
        return "NA"

    if demographics.empty == True:
        return "NA"


    count = demographics[demographics['gender'] == 'male']['face_id'].values
    if len(count) == 1:
        return str(count[0])
    else:
        return "NA"




@app.callback(
    Output("live_female_count", "children"),
    [Input("live_person_df", "children")]
)
def live_female_count_callback(person_df):

    df = pd.read_json(person_df, orient='split')

    return get_female_count(df)

def get_female_count(demographics):

    try:
        #demographics = signage_manager.live_person(signage_id)

        demographics = demographics.groupby(['gender']).aggregate({'face_id':'nunique'}).reset_index()
    except:
        return "NA"

    if demographics.empty == True:
        return "NA"


    count = demographics[demographics['gender'] == 'female']['face_id'].values
    if len(count) == 1:
        return str(count[0])
    else:
        return "NA"


@app.callback(
    Output("live_activity", "children"),
    [Input("live_person_df", "children")]
)
def live_activity_callback(person_df):
    df = pd.read_json(person_df, orient='split')

    return get_activity(df)

def get_activity(df):
    #df = signage_manager.live_person(signage_id)

    if df.empty == True:
        return "NA"
    else:
        return str(np.round(df['time_alive'].mean())) + ' seconds'


@app.callback(
    Output("live_engagement", "children"),
    [Input("live_person_df", "children")]
)
def live_engagement_callback(person_df):
    
    df = pd.read_json(person_df, orient='split')


    return get_engagement(df)

def get_engagement(df):
   
    #df = signage_manager.live_person(signage_id)

    if df.empty == True:
        return "NA"
    else:
        return str(np.round(df['engagement_range'].mean())) + ' Feet'
    

@app.callback(
    Output("live_age_group", "children"),
    [Input("live_person_df", "children")]
)
def live_agegroup_callback(person_df):
    df = pd.read_json(person_df, orient='split')

    return get_agegroup(df)

def get_agegroup(df):
   
    #df = signage_manager.live_person(signage_id)

    if df.empty == True:
        return "NA"

    ages_ = df['age'].tolist()

    return max(set(ages_), key=ages_.count)



############################# Dwell Chart ######################

@app.callback(
    Output("live_dwell_chart", "figure"),
    [Input("live_person_df", "children"), Input("live_age_group", "children")]
)
def live_dwell_callback(person_df, _):
    
    df = pd.read_json(person_df, orient='split')

    return get_live_dwell_chart(df)

def get_live_dwell_chart(df):
    #df = signage_manager.live_person(signage_id)
    if df.empty == True:
        return {'data':[],'layout':[]}

    hist_data = df['time_alive'].tolist()
    fig = ff.create_distplot([hist_data], ["Dwell time"],bin_size=[0.3],show_rug=False,colors=['#0091D5'])

    fig['layout'].update(title='Dwell Time Pockets',  yaxis={'tickformat': ',.0%','range': [0,0.6]})
    return fig




############################### Live age chart ###################

@app.callback(
    Output("live_age_chart", "figure"),
    [Input("live_person_df", "children"), Input("live_age_group", "children")]
)
def live_age_callback(person_df,_):
    df = pd.read_json(person_df, orient='split')

    return get_live_age_chart(df)


def get_live_age_chart(df):

    #df = signage_manager.live_person(signage_id)

    if df.empty == True:
        return {"data":[],"layout":[]}

    unique_age_buckets = []

    age_list = df['age'].tolist()


    counter_ = collections.Counter(age_list)

    x_labels = []
    width = []
    for ab in list(counter_.keys()):
        x_labels.append(str(ab))
        width.append(.8)

    trace1 = go.Bar(
        x=list(counter_.values()),
        y=x_labels,
        orientation = 'h',
        width = width,
    )


    data = [trace1]


    layout = go.Layout(
        xaxis=dict(showgrid=True),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title="Age Mix",    
    )

    return {"data":data,"layout":layout}


############################# Live age by gender chart #############

@app.callback(
    Output("live_agebygender_chart", "figure"),
    [Input("live_person_df", "children"), Input("live_age_group", "children")]
)
def live_agebygender_callback(person_df,_):
    
    df = pd.read_json(person_df, orient='split')

    return get_live_agebygender_chart(df)


def get_live_agebygender_chart(df):

    #df = signage_manager.live_person(signage_id)


    if df.empty == True:
        return {"data":[],"layout":[]}

    ages = df['age'].unique()

    labels = ["Male","Female"]
    male_count_list = []
    female_count_list =[]

    for age in ages:
        male_count =   df[(df['gender'] == 'male') & (df['age'] == age)]['face_id'].nunique()
        female_count = df[(df['gender'] == 'female') & (df['age'] == age) ]['face_id'].nunique()
        male_count_list.append(male_count)
        female_count_list.append(female_count)


    trace1 = go.Bar(
        x=ages,
        y=male_count_list,
        name ='Male',
    )
    trace2 = go.Bar(
        x=ages,
        y=female_count_list,
        name='Female',
    )

    data = [trace1, trace2]

    layout = go.Layout(
        xaxis=dict(showgrid=False),
        #margin=dict(l=35, r=25, b=25, t=5, pad=2),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title="Gender Count by Age",

    )

    return {"data":data,"layout":layout}




############################### Live Gender chart ###################

@app.callback(
    Output("live_gender_chart", "figure"),
    [Input("live_person_df", "children"), Input("live_age_group", "children")]
)
def live_gender_callback(person_df,_):
    df = pd.read_json(person_df, orient='split')

    return get_live_gender_chart(df)


def get_live_gender_chart(df):
    #df = signage_manager.live_person(signage_id)


    if df.empty == True:
        return {"data":[],"layout":[]}

    df = df.groupby(['gender']).aggregate({'face_id':'nunique'}).reset_index()





    male_count_ =   df[df['gender'] == 'male']['face_id'].values
    female_count_ = df[df['gender'] == 'female']['face_id'].values

    male_count = 0
    female_count = 0

    if len(male_count_) == 1:
        male_count = male_count_[0]

    if len(female_count_) == 1:
        female_count = female_count_[0]

    labels = ["Male","Female"]
    colors = {'Male': 'blue','Female':'orange'}


    trace1 = {
        "values": [male_count,female_count],
        "labels": ["Male","Female"],
        "domain": {"x": [0, 1]},
      "name": "Gender Percentage",
      "hoverinfo":"label+percent+name",
      "hole": .4,
      "type": "pie"
    }

    data = [trace1]

    layout = go.Layout(
        title="Gender Mix",
        autosize=True,
        annotations =[
            {
                "font": {
                    "size": 20
                },
                "showarrow": False,
                "text": str(male_count + female_count),

                #"x": 0.20,
                #"y": 0.5
            }]

        )

    return {"data":data,"layout":layout}

############################### Live Hourly Impressions chart ###################

@app.callback(
    Output("live_impressions_chart", "figure"),
    [Input("live_person_df", "children"), Input("live_age_group", "children")]
)
def live_impressions_callback(person_df,_):
    df = pd.read_json(person_df, orient='split')

    return get_live_impressions_chart(df)

def get_live_impressions_chart(df):

    #df = signage_manager.live_person(signage_id)

    if df.empty == True:
        return {"data":[],"layout":[]}

    df['date_created'] = pd.to_datetime(df['date_created'])

    times = pd.DatetimeIndex(df.date_created)
    df = df.groupby([times.dayofweek]).face_id.nunique()

    df = df.reset_index()

    data = [go.Bar( x=df['date_created'], y=df['face_id'], text=df['face_id'], textposition='auto',marker=dict(color='#ff8333') )]

    layout = go.Layout(
        title="Daily Impressions",
        xaxis=dict(showgrid=False,title="Day of week"),
        yaxis=dict(title="Face Count"),
        barmode='relative',
        #margin=dict(l=35, r=25, b=25, t=5, pad=2),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data":data,"layout":layout}


###################### Live Engagement Chart ########################

@app.callback(
    Output("live_engagement_chart", "figure"),
    [Input("live_person_df", "children"), Input("live_age_group", "children")]
)
def live_engagement_callback(person_df,_):
    df = pd.read_json(person_df, orient='split')

    return get_live_engagement_chart(df)



def get_live_engagement_chart(df):

    #df = signage_manager.live_person(signage_id)

    if df.empty == True:
        return {'data':[],'layout':[]}

    distances = df['engagement_range'].tolist()
    x_values = np.random.randint(low=1,high=25,size=len(distances))

    trace0 = go.Scatter(
        x = x_values,
        y = distances,
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





vertical_center = {
  "margin": 0,
  "position": "absolute",
  "top": "50%",
  "-ms-transform": "translateY(-50%)",
  "transform": "translateY(-50%)"
}

layout = [




    #indicators row
    html.Div(
        [
            indicator(
                "#00cc96",
                "Total Faces",
                "live_faces_count",

            ),
            indicator_alt(
                "#119DFF",
                "Male",
                "live_male_count",
            ),
            indicator(
                "#EF553B",
                "Female",
                "live_female_count",
            ),
            indicator_alt(
                "#00cc96",
                "Dwell time",
                "live_activity",
            ),
            indicator(
                "#119DFF",
                "Engagement Range",
                "live_engagement",
            ),
            indicator_alt(
                "#00cc96",
                "Frequent Age Group",
                "live_age_group",
            ),
        ],
        className="row",
        style={"marginTop": "5px", "max height": "200px",'border-radius': 10, 'border-color': '#ff8333'},
    ),



    # Charts
    html.Div(
        [
            
            html.Div([

            html.Div(
                [
                    dcc.Graph(
                        id = "live_engagement_chart",
                        style = {"height": "100%", "width": "98%","margin":5},
                        config = dict(displayModeBar=False),
                    ),
                ],
                style={'border':'1px solid', 'border-radius': 10,'border-color': '#1C4E80' ,'backgroundColor':'#FFFFFF'},



                ),

                 html.Div([html.P("")]),
                  html.Div([

                    dcc.Graph(
                        id = "live_age_chart",
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

                    html.Div([
                    dcc.Graph(
                        id = "live_impressions_chart",
                        style={"height": "100%", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),
                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),
                    
                    
                    html.Div([html.P("")]),

                    html.Div([
                    #html.P("        "),
                    dcc.Graph(
                        id = "live_gender_chart",
                        style={"height": "100%", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),

                    ],
                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),


                ],

                className = "four columns",



            ),

                html.Div(
                [

                    html.Div([
                    dcc.Graph(
                        id = "live_dwell_chart",
                        style={"height": "100%", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),
                    ],
                                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),

                    html.Div([html.P("")]),

                    html.Div([

                    dcc.Graph(
                        id = "live_agebygender_chart",
                        style={"height": "100%", "width": "98%","margin":5},
                        config=dict(displayModeBar=False),
                    ),
                    ],
                                    style={'border':'1px solid', 'border-radius': 10, 'border-color': '#1C4E80','backgroundColor':'#FFFFFF'},

                    ),


                ],

                className = "four columns",



            ),

        ],
        className="row",
        style={"marginTop": "5px", "max height": "600px"},
    ),

]