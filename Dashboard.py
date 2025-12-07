# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site}
                 for site in spacex_df['Launch Site'].unique()],
        value='ALL',  # default selection
        placeholder="Select Launch Site",
        searchable=True
    ),

    html.Br(),

    # TASK 2: Pie chart for successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        value=[min_payload, max_payload],
        marks={
            int(min_payload): str(int(min_payload)),
            int(max_payload): str(int(max_payload))
        }
    ),

    html.Br(),

    # TASK 4: Scatter chart for payload vs launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    # Case 1: All sites – pie shows successful launches per site
    if selected_site == 'ALL':
        # Filter only successful launches
        df_success = spacex_df[spacex_df['class'] == 1]

        fig = px.pie(
            df_success,
            names='Launch Site',          # slice per site
            title='Total Successful Launches by Site'
        )
        return fig

    # Case 2: Specific site – pie shows success vs failure for that site
    else:
        # Filter for just that site
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]

        # Get counts of success(1)/failure(0)
        outcome_counts = df_site['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']

        fig = px.pie(
            outcome_counts,
            values='count',               # counts per outcome
            names='class',                # 0 = Fail, 1 = Success
            title=f'Success vs Failure for Site: {selected_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs,
# `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range

    # Filter by payload range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    # Filter by site if not ALL
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f'Payload vs. Success for {selected_site}'
    else:
        title = 'Payload vs. Success for All Sites'

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
