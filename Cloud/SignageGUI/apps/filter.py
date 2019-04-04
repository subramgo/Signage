import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from app import app, server, signage_manager, app_state
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
enterprise_drops = signage_manager.get_enterprise()

logging.info(app_state.print())

layout =[




        html.Div([

          html.Div([

        html.Div([html.P("Enterprise")]),

        html.Div([
             dcc.Dropdown(
            id='enterprise-dropdown',
            options=app_state.enterprise_options(),
            value = app_state.enterprise_id,
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
                                                     clearable=True,
                                                     #options = app_state.store_options(app_state.enterprise_id),
                                                     #value = app_state.store_id,


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
                                              #options = app_state.signage_options(app_state.store_id),
                                              
                                              #value = app_state.signage_id,

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
    Output("selected_enterprise_df", "children"),
    [Input("switch-button", "n_clicks")]
)
def button_callback(nclicks):

    logger.info("Enterprise id " + str(app_state.enterprise_id))
    logger.info("Store id " + str(app_state.store_id))
    logger.info("singage id " + str(app_state.signage_id))

    df = signage_manager.live_person(app_state.signage_id)
    app_state.live_person_df = df

    df = signage_manager.overall_effectiveness(app_state.signage_id)
    app_state.effectiveness_df = df

    df = signage_manager.get_recommendation(app_state.signage_id)
    app_state.recommendation_df = df


    df = signage_manager.person_all_signage(app_state.store_id)
    app_state.person_all_signage_df = df

    logger.info(df['location'].unique())

    logger.info("Data set created")

    return None

@app.callback(
    Output("live_person_df", "children"),
    [Input("signage-dropdown", "value")]
)
def live_person_df_callback(signage_id):

    signage_id = int(signage_id)

    app_state.signage_id = signage_id
    return None

##################################### Update Signage #########################


@app.callback(
    Output('signage-dropdown', 'value'),
    [Input('store-dropdown', 'value')])
def load_signage_value(store_id):

    store_id = int(store_id)

    if app_state.store_id != store_id:
        app_state.store_id = store_id
        return app_state.signage_value(store_id)
    else:
       return app_state.signage_id



@app.callback(
    Output('signage-dropdown', 'options'),
    [Input('store-dropdown', 'value')])
def load_signage_option(store_id):

           store_id = int(store_id)

           if app_state.store_id != store_id:
               app_state.store_id = store_id
           
           return app_state.signage_options(store_id)

############# Update Store #######################


@app.callback(
    Output('store-address', 'children'),
    [Input('store-dropdown', 'value')])
def load_stores_address(store_id):

       store_id = int(store_id)
       app_state.store_id = store_id
       return app_state.store_address(store_id)


@app.callback(
    Output('store-dropdown', 'options'),
    [Input('enterprise-dropdown', 'value')])
def load_stores_options(in_enterprise_id):

    in_enterprise_id = int(in_enterprise_id)
    if app_state.enterprise_id != in_enterprise_id:
        app_state.enterprise_id = in_enterprise_id
    
    return app_state.store_options(in_enterprise_id)



@app.callback(
    Output('store-dropdown', 'value'),
    [Input('enterprise-dropdown', 'value')])
def load_stores_value(in_enterprise_id):

    in_enterprise_id = int(in_enterprise_id)

    if app_state.enterprise_id != in_enterprise_id:
        app_state.enterprise_id = in_enterprise_id
        return app_state.store_value(in_enterprise_id)
    else:
        return app_state.store_id








