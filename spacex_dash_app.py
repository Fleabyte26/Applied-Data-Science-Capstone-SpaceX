# app.py
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load the SpaceX dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get unique launch sites
launch_sites = spacex_df['Launch Site'].unique().tolist()

# Calculate payload range for slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign': 'center'}),
    html.Br(),

    # Launch Site Dropdown
    html.Label("Select Launch Site:"),
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                [{'label': site, 'value': site} for site in launch_sites],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # Success Pie Chart
    dcc.Graph(id='success-pie-chart'),
    html.Br(),

    # Payload Range Slider
    html.Label("Select Payload Range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # Success vs Payload Scatter Chart
    dcc.Graph(id='success-payload-scatter-chart'),

    html.H2("Launch Insights"),
    # New Bar Charts
    dcc.Graph(id='site-success-bar'),
    dcc.Graph(id='site-success-rate-bar'),
    dcc.Graph(id='payload-success-rate-bar'),
    dcc.Graph(id='booster-success-rate-bar')
])

# Callback for success pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df, 
            names='Launch Site', 
            values='class', 
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered_df, 
            names='class', 
            title=f"Success vs Failure for site {selected_site}"
        )
    return fig

# Callback for payload-success scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df, x='Payload Mass (kg)', y='class',
        color='Booster Version Category',
        title='Payload vs Launch Outcome'
    )
    return fig

# Callback for new insights bar charts
@app.callback(
    [Output('site-success-bar', 'figure'),
     Output('site-success-rate-bar', 'figure'),
     Output('payload-success-rate-bar', 'figure'),
     Output('booster-success-rate-bar', 'figure')],
    Input('site-dropdown', 'value')
)
def update_insight_charts(selected_site):
    # Site success count
    site_success = spacex_df[spacex_df['class'] == 1].groupby('Launch Site')['class'].count().reset_index()
    fig_site_success = px.bar(site_success, x='Launch Site', y='class', title='Successful Launches by Site')

    # Site success rate
    site_rate = spacex_df.groupby('Launch Site')['class'].mean().reset_index()
    fig_site_rate = px.bar(site_rate, x='Launch Site', y='class', title='Launch Success Rate by Site')

    # Payload success rate
    bins = [0, 2500, 5000, 7500, 10000]
    labels = ['0-2500', '2500-5000', '5000-7500', '7500-10000']
    spacex_df['Payload Range'] = pd.cut(spacex_df['Payload Mass (kg)'], bins=bins, labels=labels)
    payload_rate = spacex_df.groupby('Payload Range')['class'].mean().reset_index()
    fig_payload_rate = px.bar(payload_rate, x='Payload Range', y='class', title='Launch Success Rate by Payload Range')

    # Booster success rate
    booster_rate = spacex_df.groupby('Booster Version Category')['class'].mean().reset_index()
    fig_booster_rate = px.bar(booster_rate, x='Booster Version Category', y='class', title='Launch Success Rate by Booster Version')

    return fig_site_success, fig_site_rate, fig_payload_rate, fig_booster_rate

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)

