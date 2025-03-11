import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Load the comparison data from the Excel file
df = pd.read_excel(r"C:\Users\adity\Downloads\Major Project\Efficiency-app\Technical_Comparison_2013_2023.xlsx", sheet_name="Sheet1")

# Dash App Initialization
app = dash.Dash(__name__)
app.title = "Efficiency Analysis"

template = "plotly_white"
app.layout = html.Div([
    html.H1("Efficiency Analysis and Mechanical Life Estimation", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            html.Label("⚙️ Select Technical Parameter"),
            dcc.Dropdown(
                id='parameter-dropdown',
                options=[{'label': param, 'value': param} for param in df["Technical Parameters"]],
                value=df["Technical Parameters"].iloc[0],
                clearable=False
            ),
            dcc.Graph(id='comparison-graph'),
        ], style={'width': '90%', 'textAlign': 'center', 'marginTop': '50px', 'border': '2px solid black', 'padding': '20px'}),
        
        
    ]),
    
    html.Div([
        html.H2("📈 Yearly Month-wise Comparison"),
        html.Label("⚙️ Select Technical Parameter for Yearly Month-wise Comparison"),
        dcc.Dropdown(
            id='yearwise-parameter-dropdown',
            options=[{'label': param, 'value': param} for param in df["Technical Parameters"]],
            value=df["Technical Parameters"].iloc[0],
            clearable=False
        ),
        dcc.Graph(id='yearwise-line-graph'),
    ], style={'width': '100%', 'textAlign': 'center', 'marginTop': '50px', 'border': '2px solid black', 'padding': '20px'}),
    
    html.Div([
        html.H2("🔩 Mechanical Life Estimation"),
        html.Div([
            html.Label("Usage Hours per Year:"),
            dcc.Input(id='usage-hours', type='number', value=4863, min=1000, max=8000, step=5, style={'float': 'right'}),
            html.Br(), html.Br(),
            
            html.Label("Stress Cycles per Year:"),
            dcc.Input(id='stress-cycles', type='number', value=200000, min=50000, max=1000000, step=50, style={'float': 'right'}),
            html.Br(), html.Br(),
            
            html.Label("Operating Temperature (°C):"),
            dcc.Input(id='temperature', type='number', value=515, min=100, max=600, step=1, style={'float': 'right'}),
            html.Br(), html.Br(),
            
            html.Button("Calculate", id='calculate-button', n_clicks=0, style={'marginTop': '10px', 'display': 'block', 'margin': 'auto'}),
            html.Br(), html.Br(),
            
            html.Label("Ans:"),
            html.Div(id='life-estimation-output', style={'border': '1px solid black', 'padding': '10px', 'marginTop': '10px', 'fontSize': '18px'})
        ], style={'border': '2px solid black', 'padding': '20px', 'width': '75%', 'margin': 'auto', 'textAlign': 'left'})
    ], style={'width': '100%', 'textAlign': 'center', 'marginTop': '50px'})
])

# Callbacks for interactivity
@app.callback(
    Output('comparison-graph', 'figure'),
    [Input('parameter-dropdown', 'value')]
)
def update_graph(parameter):
    selected_data = df[df["Technical Parameters"] == parameter]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["2013", "2023"], y=selected_data.iloc[0, 1:],
                         marker=dict(color=['blue', 'green'])))
    
    value_2013, value_2023 = selected_data.iloc[0, 1], selected_data.iloc[0, 2]
    percentage_change = ((value_2023 - value_2013) / value_2013) * 100 if value_2013 != 0 else 0
    annotation_text = f"{percentage_change:.2f}% change"
    
    fig.add_annotation(
        x="2023", y=value_2023,
        text=annotation_text,
        showarrow=True,
        arrowhead=2,
        font=dict(size=14, color="red"),
    )
    
    fig.update_layout(title=f"Comparison of {parameter} (2013 vs 2023)",
                      yaxis_title=parameter, template=template)
    return fig

@app.callback(
    Output('summary-bar-chart', 'figure'),
    [Input('parameter-dropdown', 'value')]
)
def update_summary_charts(parameter):
    bar_fig = go.Figure()
    for param in df["Technical Parameters"]:
        bar_fig.add_trace(go.Bar(x=["2013", "2023"], y=df[df["Technical Parameters"] == param].iloc[0, 1:], name=param))
    
    bar_fig.update_layout(title="Overall Parameter Comparison", template=template, barmode='group')
    
    return bar_fig

@app.callback(
    Output('yearwise-line-graph', 'figure'),
    [Input('yearwise-parameter-dropdown', 'value')]
)
def update_yearwise_line_graph(parameter):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    # Simulating monthly data for 2013 and 2023
    np.random.seed(42)
    data_2013 = np.random.normal(df[df["Technical Parameters"] == parameter].iloc[0, 1], 1, 12)
    data_2023 = np.random.normal(df[df["Technical Parameters"] == parameter].iloc[0, 2], 1, 12)
    
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(x=months, y=data_2013, mode='lines+markers', name='2013'))
    line_fig.add_trace(go.Scatter(x=months, y=data_2023, mode='lines+markers', name='2023'))
    
    line_fig.update_layout(title=f"Monthly Comparison of {parameter} (2013 vs 2023)",
                           yaxis_title=parameter, template=template)
    
    return line_fig

@app.callback(
    Output('life-estimation-output', 'children'),
    [Input('calculate-button', 'n_clicks')],
    [State('usage-hours', 'value'),
     State('stress-cycles', 'value'),
     State('temperature', 'value')]
)
def estimate_life(n_clicks, usage_hours, total_stress_cycles, operating_temp):
    if n_clicks > 0:
        temperature_k = operating_temp + 273
        C = 20  # Larson-Miller Constant (Material Dependent)
        life_remaining_years = (C * (100000 / total_stress_cycles)) * (1000 / usage_hours) * (600 / temperature_k)
        
        years = int(life_remaining_years)
        months = int((life_remaining_years - years) * 12)
        days = int(((life_remaining_years - years) * 12 - months) * 30)
        
        component = "Bearings and Rotating Components" if total_stress_cycles > 500000 else "Boiler Tubes and Heat Exchangers"
        
        return f"🔍 Estimated Remaining Life: {years} years, {months} months, {days} days. \nLikely first wear-out component: {component}"
    return ""

if __name__ == '__main__':import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Load the comparison data from the Excel file
df = pd.read_excel(r"C:\Users\adity\Downloads\Major Project\Efficiency-app\Technical_Comparison_2013_2023.xlsx", sheet_name="Sheet1")

# Dash App Initialization
app = dash.Dash(__name__)
app.title = "Efficiency Analysis"

template = "plotly_white"
app.layout = html.Div([
    html.H1("Efficiency Analysis and Mechanical Life Estimation", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            html.Label("⚙️ Select Technical Parameter"),
            dcc.Dropdown(
                id='parameter-dropdown',
                options=[{'label': param, 'value': param} for param in df["Technical Parameters"]],
                value=df["Technical Parameters"].iloc[0],
                clearable=False
            ),
            dcc.Graph(id='comparison-graph'),
        ], style={'width': '90%', 'textAlign': 'center', 'marginTop': '50px', 'border': '2px solid black', 'padding': '20px'}),
        
    ]),
    
    html.Div([
        html.H2("📈 Yearly Month-wise Comparison"),
        html.Label("⚙️ Select Technical Parameter for Yearly Month-wise Comparison"),
        dcc.Dropdown(
            id='yearwise-parameter-dropdown',
            options=[{'label': param, 'value': param} for param in df["Technical Parameters"]],
            value=df["Technical Parameters"].iloc[0],
            clearable=False
        ),
        dcc.Graph(id='yearwise-line-graph'),
    ], style={'width': '100%', 'textAlign': 'center', 'marginTop': '50px', 'border': '2px solid black', 'padding': '20px'}),
    
    html.Div([
        html.H2("🔩 Mechanical Life Estimation"),
        html.Div([
            html.Label("Usage Hours per Year"),
            dcc.Input(id='usage-hours', type='number', value=4863, min=1000, max=8000, step=20, style={'width': '100%'}),
            
            html.Label("Stress Cycles per Year"),
            dcc.Input(id='stress-cycles', type='number', value=200000, min=50000, max=1000000, step=200, style={'width': '100%'}),
            
            html.Label("Operating Temperature (°C)"),
            dcc.Input(id='temperature', type='number', value=515, min=100, max=600, step=5, style={'width': '100%'}),
            
            html.Button("Calculate Life", id='calculate-button', n_clicks=0, style={'marginTop': '10px', 'width': '100%'}),
            
            html.Div(id='life-estimation-output', style={'marginTop': '20px', 'fontSize': '18px', 'width': '100%'})
        ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top', 'textAlign': 'right'})
    ]),
])

# Callbacks for interactivity
@app.callback(
    Output('comparison-graph', 'figure'),
    [Input('parameter-dropdown', 'value')]
)
def update_graph(parameter):
    selected_data = df[df["Technical Parameters"] == parameter]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["2013", "2023"], y=selected_data.iloc[0, 1:],
                         marker=dict(color=['blue', 'green'])))
    fig.update_layout(title=f"Comparison of {parameter} (2013 vs 2023)",
                      yaxis_title=parameter, template=template)
    return fig

@app.callback(
    Output('summary-bar-chart', 'figure'),
    [Input('parameter-dropdown', 'value')]
)
def update_summary_charts(parameter):
    bar_fig = go.Figure()
    for param in df["Technical Parameters"]:
        bar_fig.add_trace(go.Bar(x=["2013", "2023"], y=df[df["Technical Parameters"] == param].iloc[0, 1:], name=param))
    
    bar_fig.update_layout(title="Overall Parameter Comparison", template=template, barmode='group')
    
    return bar_fig

@app.callback(
    Output('yearwise-line-graph', 'figure'),
    [Input('yearwise-parameter-dropdown', 'value')]
)
def update_yearwise_line_graph(parameter):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    # Simulating monthly data for 2013 and 2023
    np.random.seed(42)
    data_2013 = np.random.normal(df[df["Technical Parameters"] == parameter].iloc[0, 1], 1, 12)
    data_2023 = np.random.normal(df[df["Technical Parameters"] == parameter].iloc[0, 2], 1, 12)
    
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(x=months, y=data_2013, mode='lines+markers', name='2013'))
    line_fig.add_trace(go.Scatter(x=months, y=data_2023, mode='lines+markers', name='2023'))
    
    line_fig.update_layout(title=f"Monthly Comparison of {parameter} (2013 vs 2023)",
                           yaxis_title=parameter, template=template)
    
    return line_fig

@app.callback(
    Output('life-estimation-output', 'children'),
    [Input('calculate-button', 'n_clicks')],
    [State('usage-hours', 'value'),
     State('stress-cycles', 'value'),
     State('temperature', 'value')]
)
def estimate_life(n_clicks, usage_hours, total_stress_cycles, operating_temp):
    if n_clicks > 0:
        temperature_k = operating_temp + 273
        C = 20  # Larson-Miller Constant (Material Dependent)
        life_remaining_years = (C * (100000 / total_stress_cycles)) * (1000 / usage_hours) * (600 / temperature_k)
        
        years = int(life_remaining_years)
        months = int((life_remaining_years - years) * 12)
        days = int(((life_remaining_years - years) * 12 - months) * 30)
        
        if total_stress_cycles > 700000:
            component = "Bearings and Rotating Components"
        elif 400000 <= total_stress_cycles <= 700000 and operating_temp > 500:
            component = "Boiler Tubes and Heat Exchangers"
        elif 200000 <= total_stress_cycles < 400000 and operating_temp > 450:
            component = "Turbine Blades and Compressor Components"
        elif usage_hours > 6000:
            component = "Piping and Structural Components"
        else:
            component = "General Mechanical Components"

        return f"🔍 Estimated Remaining Life: {years} years, {months} months, {days} days.\nLikely first wear-out component: {component}"
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
    app.run_server(debug=True)