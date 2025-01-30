# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_list = launch_sites_df['Launch Site'].tolist()
import numpy as np
#sucess_by_site_ = spacex_df.groupby('Launch Site')['class'].apply(lambda x: (x==1).sum()).reset_index('Launch Site')#.sum().reset_index()
#sucess_by_site = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
sucess_by_site = spacex_df.loc[spacex_df['class'] == 1][['Launch Site','class']]
sucess_by_site = sucess_by_site.groupby('Launch Site')['class'].sum().reset_index()
#sucess_by_site = spacex_df[['Launch Site','class'==1]]#.reset_index(inplace=True)
#sucess_by_site  = sucess_by_site.reset_index(inplace=True)
""" sucess_by_site = sucess_by_site.query('class == 1') """
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', options=[{'label': 'All Sites', 'value': 'ALL'}  # Static option
                                    ] + [{'label': sSite, 'value': sSite} for sSite in launch_sites_list],  # List comprehension for dynamic options
                                    placeholder='Select a Launch Site here',
                                    value='ALL',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart',
                                                   figure=px.pie(sucess_by_site,
                                                   values='class',
                                                   names = 'Launch Site',
                                                   title='Launches For all sites'
                                                       
                                                   ))),
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    #marks={0: '0', 1000: '1000'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='Launches For all sites')
        fig.update_layout(title='Launches For all sites')
        return fig
    else:
        filtered_df = spacex_df.loc[spacex_df['Launch Site'] == entered_site][['Launch Site','class']]
        filtered_df = filtered_df.value_counts().reset_index()
        filtered_df["class"] = filtered_df["class"].replace({0: "Failure", 1: "Success"})
        fig = px.pie(filtered_df, values='count', 
        names='class', 
        title=f'Launches For site {entered_site}',
        color="class", 
        labels={'Failure': 'Fail', 'Success': 'Success'},
        color_discrete_map={
            'Failure': 'red',
            'Success': 'green'}
        )
        fig.update_traces(textinfo="percent+label", pull=[0, 0.1, 0, 0])
        fig.update_layout(title=f'Launches For site {entered_site}')
        return fig
        # return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_mass):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        min_value = payload_mass[0]
        max_value = payload_mass[1]
        filtered_df = spacex_df[(spacex_df["Payload Mass (kg)"] >= min_value) & (spacex_df["Payload Mass (kg)"] <= max_value)]
        fig_s = px.scatter(filtered_df, x="Payload Mass (kg)", y="class",
                           color="Booster Version Category")
        return fig_s
    else:
        min_value = payload_mass[0]
        max_value = payload_mass[1]
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) & (spacex_df["Payload Mass (kg)"] >= min_value) & (spacex_df["Payload Mass (kg)"] <= max_value)]
        fig_s = px.scatter(filtered_df, x="Payload Mass (kg)", y="class",
                           color="Booster Version Category")
        return fig_s

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
