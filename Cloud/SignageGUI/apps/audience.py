import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from .insights import group, overall, demographics, recommendations
from app import signage_manager, app
import dash_table

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'

}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#1C4E80',
    'color': 'white',
    'padding': '6px'
}

layout =[
        
        html.Div([

            dcc.Tabs(
                id="audience_tabs",
                value="audience_effect_tab",
                children=[
                    dcc.Tab(label="Overall Effectiveness", value="audience_effect_tab",style=tab_style, selected_style=tab_selected_style),
                    dcc.Tab(label="Demographics Effectiveness", value="audience_demo_effect_tab",style=tab_style, selected_style=tab_selected_style),
                    dcc.Tab(label="Recommendation", value="recommendation_tab",style=tab_style, selected_style=tab_selected_style),


                ]
            ,style=tabs_styles)

            ],
           # className="row",style={"margin": "2% 3%"}
        ),
        
        html.Div(id="audience_tab_content"),#, className="row", style={"margin": "2% 3%"}),


]

@app.callback(Output("audience_tab_content", "children"), [Input("audience_tabs", "value")])
def render_content(tab):
    if tab == "audience_effect_tab":
        return overall.layout
    elif tab == "audience_demo_effect_tab":
        return demographics.layout
    elif tab == "recommendation_tab":
    	return recommendations.layout