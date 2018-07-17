# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
from nptdms import TdmsFile
from nptdms import tdms
from nptdms import TdmsFile
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from math import ceil
from plotly import tools

sensor_list = {'Thermocouples': {0: ['Nitrous Tank Temp', 'ai0', 'OTC1', 'degC'], 1: ['Combustion Chamber Temp', 'ai1', 'OTC2', 'degC'], 2: ['Throat Temp', 'ai2', 'OTC3', 'degC'], 3: ['Exit Temp', 'ai3', 'OTC4', 'degC']}, 'PT and LC': {0: ['Thrust', 'ai0', 'LC5', 'lb'], 1: ['Accumulator Scale', 'ai1', 'LC1-4', 'lb'], 2: ['Tank Pressure', 'ai2', 'OPT1', 'psi'], 3: ['Feed Pressure', 'ai3', 'OPT2', 'psi'], 4: ['Chamber Pressure', 'ai4', 'OPT3', 'psi'], 5: ['Nitrogen Line Pressure', 'ai5', 'NPT1', 'psi'], 6: ['Pnuematic Line Pressure', 'ai6', 'NPT2', 'psi']}}

temp_data = []
temp_time = []
temp_file = TdmsFile("ai_temp_data.tdms")
temp_titles = []
for key in sensor_list['Thermocouples']:
    channel = temp_file.object('_unnamedTask<1>', 'cDAQsimMod1/' + sensor_list['Thermocouples'][key][1])
    temp_data.append(channel.data)
    temp_time.append(channel.time_track())
    temp_titles.append(sensor_list['Thermocouples'][key][0])

PTLC_data = [-5,-3,3,6,2,7,9,7,0,6]
PTLC_time = [-1,0,1,2,3,4,5,6,7,8]
PTLC_titles = []
# PTLC_file = TdmsFile("ls_data.tdms")
# #volt_file = TdmsFile("ai_voltage_data.tdms")
for key in sensor_list['PT and LC']:
    PTLC_titles.append(sensor_list['PT and LC'][key][0])
#     channel = temp_file.object('_unnamedTask<2>', 'cDAQsimMod2/' + sensor_list['PT and LC'][key][1])
#     PTLC_data.append(channel.data)
#     PTLC_time.append(channel.time_track())

all_titles = temp_titles + PTLC_titles

app = dash.Dash()

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
Logo = 'Logo.png'
encoded_image = base64.b64encode(open(Logo, 'rb').read())

## Data preprocessing 
traces = []
allrowsn = int(ceil((len(sensor_list['Thermocouples']) + len(sensor_list['PT and LC']))/2.0))
all_fig = tools.make_subplots(rows=allrowsn, cols=2, subplot_titles=all_titles)
titles=[]
for i in range(len(sensor_list['Thermocouples'])):
    traces.append(go.Scatter(
        x=temp_time[i],
        y=temp_data[i],
    ))
    titles.append(sensor_list['Thermocouples'][i][0])
for i in range(len(sensor_list['PT and LC'])):
    traces.append(go.Scatter(
        x=PTLC_time,
        y=PTLC_data,
    ))
    titles.append(sensor_list['PT and LC'][i][0])
count = 0
for i in range(allrowsn):
    for j in range(2):
        if count >= len(sensor_list['Thermocouples']) + len(sensor_list['PT and LC']):
            break
        all_fig['layout']['annotations'][count]['font'].update(color='#ffffff')
        all_fig.append_trace(traces[count], i+1, j+1)
        all_fig['layout']['xaxis'+str(count + 1)].update(title='Time', showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        if count < len(sensor_list['Thermocouples']):
            all_fig['layout']['yaxis'+str(count + 1)].update(title=sensor_list['Thermocouples'][count][3], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        else:
            all_fig['layout']['yaxis'+str(count + 1)].update(title=sensor_list['PT and LC'][count-len(sensor_list['Thermocouples'])][3], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        count += 1

all_fig['layout'].update(title='All Plots', height=400*allrowsn, showlegend=False, paper_bgcolor='#333f48', plot_bgcolor='#ffffff', titlefont={'color':'#ffffff'})

traces = []
n = len(sensor_list['Thermocouples'])
rowsn= int(ceil(n/2.0))
temp_fig = tools.make_subplots(rows=rowsn, cols=2, subplot_titles=temp_titles)
titles=[]
for i in range(len(sensor_list['Thermocouples'])):
    traces.append(go.Scatter(
        x=temp_time[i],
        y=temp_data[i],
    ))
    titles.append(sensor_list['Thermocouples'][i][0])
count = 0
for i in range(rowsn):
    for j in range(2):
        if count >= n:
            break
        temp_fig['layout']['annotations'][count]['font'].update(color='#ffffff')
        temp_fig.append_trace(traces[count], i+1, j+1)
        temp_fig['layout']['xaxis'+str(count + 1)].update(title='Time', showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        temp_fig['layout']['yaxis'+str(count + 1)].update(title=sensor_list['Thermocouples'][count][3], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        count += 1

temp_fig['layout'].update(title='Temperature Plots', height=400*rowsn, showlegend=False, paper_bgcolor='#333f48', plot_bgcolor='#ffffff', titlefont={'color':'#ffffff'})

traces = []
n = len(sensor_list['PT and LC'])
rowsn= int(ceil(n/2.0))
PTLC_fig = tools.make_subplots(rows=rowsn, cols=2, subplot_titles=PTLC_titles)
titles=[]
for i in range(len(sensor_list['PT and LC'])):
    traces.append(go.Scatter(
        # x=PTLC_time[i],
        # y=PTLC_data[i],
        x=PTLC_time,
        y=PTLC_data,
    ))
    titles.append(sensor_list['PT and LC'][i][0])
count = 0
for i in range(rowsn):
    for j in range(2):
        if count >= n:
            break
        PTLC_fig['layout']['annotations'][count]['font'].update(color='#ffffff')
        PTLC_fig.append_trace(traces[count], i+1, j+1)
        PTLC_fig['layout']['xaxis'+str(count + 1)].update(title='Time', showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        PTLC_fig['layout']['yaxis'+str(count + 1)].update(title=sensor_list['PT and LC'][count][3], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        count += 1

PTLC_fig['layout'].update(title='Pressure Transducer and Load Cell Plots', height=400*rowsn, showlegend=False, paper_bgcolor='#333f48', plot_bgcolor='#ffffff', titlefont={'color':'#ffffff'})

## Dash code
app.layout = html.Div(id='Page', children=[
    html.Header(className='row', style={'vertical-align':'middle'}, children=[
        html.Img(id='Logo', style={'width':'5%', 'height':'10%', 'float':'left'}, src='data:image/png;base64,{}'.format(encoded_image.decode())),
        html.Div(id='Title', style={'text-align':'center', 'float':'center'}, children=[
            html.H1(style={'color':'#333f48'}, children='Test Analysis and Run Program')
                ]),
        # html.Div(id='SidebarToggle', className='three columns')
        ]),
    html.Main(id='PlotPanel', children=[
        html.Div(id='PlotlPanelHeader', style={'vertical-align':'middle'}, className='row', children=[
            html.Div(id='PlotPanelTitle', style={'text-align':'center', 'float':'center'}, children=[
                html.H2(style={'color':'#bf5700'}, children='Plots')
                ]),
            html.Div(style={'float':'right', 'margin-bottom':'2px', 'width':'20%'}, children=[
                dcc.Dropdown(
                    id='my-dropdown',
                    options=[
                        {'label': 'Temperature Plots', 'value': 'Temp'},
                        {'label': 'Transducer and Load Cell Plots', 'value': 'PTLC'},
                        {'label': 'All Plots', 'value': 'All'}
                    ],
                    value='Temp'
                ),
            ])
        ]),
        html.Div(id='Plots', className='twelve columns', children=dcc.Graph(id='plots'), style={'border': '6px solid #bf5700'}),
    ]),
    html.Div(className='Sidebar')
])


@app.callback(
    Output(component_id='plots', component_property='figure'),
    [Input(component_id='my-dropdown', component_property='value')]
    )
def update_Plots(input_value):
    if input_value=='Temp':
        return temp_fig
    if input_value=='PTLC':
        return PTLC_fig
    if input_value=='All':
        return all_fig

if __name__ == '__main__':
    app.run_server(debug=True)