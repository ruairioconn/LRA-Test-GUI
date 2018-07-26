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
import math
from plotly import tools
import numpy as np
from scipy import optimize

#############################################################################################################################################################################################
#Dictionary of sensor metadata:
sensor_list = {'Thermocouples': {0: ['Nitrous Tank Temp', 'ai0', 'OTC1', 'degC'], 1: ['Combustion Chamber Temp', 'ai1', 'OTC2', 'degC'], 2: ['Throat Temp', 'ai2', 'OTC3', 'degC'], 3: ['Exit Temp', 'ai3', 'OTC4', 'degC']}, 'PT and LC': {0: ['Mass Flow Rate', 'null', 'null', 'lb/s'], 1: ['Thrust', 'ai0', 'LC5', 'lb'], 2: ['Accumulator Scale', 'ai1', 'LC1-4', 'lb'], 3: ['Tank Pressure', 'ai2', 'OPT1', 'psi'], 4: ['Feed Pressure', 'ai3', 'OPT2', 'psi'], 5: ['Chamber Pressure', 'ai4', 'OPT3', 'psi'], 6: ['Nitrogen Line Pressure', 'ai5', 'NPT1', 'psi'], 7: ['Pnuematic Line Pressure', 'ai6', 'NPT2', 'psi']}}

#############################################################################################################################################################################################
#Import data from TDMS files:
temp_data = []
temp_time = []
temp_file = TdmsFile("ai_temp_data.tdms")
temp_titles = []
for key in sensor_list['Thermocouples']:
    channel = temp_file.object('_unnamedTask<1>', 'cDAQsimMod1/' + sensor_list['Thermocouples'][key][1])
    temp_data.append(channel.data)
    temp_time.append(channel.time_track())
    temp_titles.append(sensor_list['Thermocouples'][key][0])

raw_PTLC_data = [-5,-3,3,6,2,7,9,7,0,6]
raw_PTLC_time = [-1,0,1,2,3,4,5,6,7,8]
PTLC_data = []
PTLC_time = []
PTLC_titles = []
# PTLC_file = TdmsFile("ls_data.tdms")
# #volt_file = TdmsFile("ai_voltage_data.tdms")
for key in sensor_list['PT and LC']:
    PTLC_titles.append(sensor_list['PT and LC'][key][0])
#     channel = temp_file.object('_unnamedTask<2>', 'cDAQsimMod2/' + sensor_list['PT and LC'][key][1])
    PTLC_data.append(raw_PTLC_data)
    PTLC_time.append(raw_PTLC_time)

PTLC_data[0] = np.gradient(PTLC_data[2])

all_titles = temp_titles + PTLC_titles

#############################################################################################################################################################################################
#Need to find start and finish points of engine fire and readjust the time column
starttime=2
endtime=4


#############################################################################################################################################################################################
#Data for table:
MassFlowRate = np.mean(PTLC_data[0])
BurnTime = 8
Impulse = np.trapz(PTLC_data[1], PTLC_time[1])
Isp = Impulse/(MassFlowRate*9.8)
PeakThrust = max(PTLC_data[1])
AvgThrust = Impulse/BurnTime
ThrustVariance = np.var(PTLC_data[1])
PeakChamberPress = max(PTLC_data[5])
AvgChamberPress = np.trapz(PTLC_data[5], PTLC_time[5])/BurnTime
ChamberPressVariance = np.var(PTLC_data[5])

#############################################################################################################################################################################################
#Create table figure:
table_trace = go.Table(
    header=dict(values=['Mass Flow Rate', 'Isp', 'Burn Time', 'Impulse', 'Avg Thrust', 'Peak Thrust', 'Thrust Variance', 'Average Chamber Pressure', 'Peak Chamber Pressure', 'Chamber Pressure Variance'],
                line = dict(color='#7D7F80'),
                fill = dict(color='#a1c3d1'),
                align = ['left'] * 5),
    cells=dict(values=[MassFlowRate, Isp, BurnTime, Impulse, AvgThrust, PeakThrust, ThrustVariance, AvgChamberPress, PeakChamberPress, ChamberPressVariance],
               line = dict(color='#7D7F80'),
               fill = dict(color='#EDFAFF'),
               align = ['left'] * 5))

table_layout = dict(width=1500, height=300)
table_data = [table_trace]
table_fig = dict(data=table_data, layout=table_layout)

#############################################################################################################################################################################################
#Create plot figures for each dropdown value:
traces = []
allrowsn = int(math.ceil((len(sensor_list['Thermocouples']) + len(sensor_list['PT and LC']))/2.0))
all_fig = tools.make_subplots(rows=allrowsn, cols=2, subplot_titles=all_titles)
titles=[]
for i in range(len(sensor_list['Thermocouples'])):
    traces.append(go.Scatter(
        x=temp_time[i],
        y=temp_data[i],
        hoverinfo='y'
    ))
    titles.append(sensor_list['Thermocouples'][i][0])
for i in range(len(sensor_list['PT and LC'])):
    traces.append(go.Scatter(
        x=PTLC_time[i],
        y=PTLC_data[i],
        hoverinfo='y'
        ))
    titles.append(sensor_list['PT and LC'][i][0])
count = 0
for i in range(allrowsn):
    for j in range(2):
        if count >= len(sensor_list['Thermocouples']) + len(sensor_list['PT and LC']):
            break
        all_fig['layout']['annotations'][count]['font'].update(color='#ffffff')
        all_fig.append_trace(traces[count], i+1, j+1)
        all_fig['layout']['xaxis'+str(count + 1)].update(title='Time', showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2, range=[starttime, endtime])
        if count < len(sensor_list['Thermocouples']):
            all_fig['layout']['yaxis'+str(count + 1)].update(title=sensor_list['Thermocouples'][count][3], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        else:
            all_fig['layout']['yaxis'+str(count + 1)].update(title=sensor_list['PT and LC'][count-len(sensor_list['Thermocouples'])][3], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        count += 1

all_fig['layout'].update(title='All Plots', height=400*allrowsn, showlegend=False, paper_bgcolor='#333f48', plot_bgcolor='#ffffff', titlefont={'color':'#ffffff'})

traces = []
n = len(sensor_list['Thermocouples'])
rowsn= int(math.ceil(n/2.0))
temp_fig = tools.make_subplots(rows=rowsn, cols=2, subplot_titles=temp_titles)
titles=[]
for i in range(len(sensor_list['Thermocouples'])):
    traces.append(go.Scatter(
        x=temp_time[i],
        y=temp_data[i],
        hoverinfo='y'
    ))
    titles.append(sensor_list['Thermocouples'][i][0])
count = 0
for i in range(rowsn):
    for j in range(2):
        if count >= n:
            break
        temp_fig['layout']['annotations'][count]['font'].update(color='#ffffff')
        temp_fig.append_trace(traces[count], i+1, j+1)
        temp_fig['layout']['xaxis'+str(count + 1)].update(title='Time', showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2, range=[starttime, endtime])
        temp_fig['layout']['yaxis'+str(count + 1)].update(title=sensor_list['Thermocouples'][count][3], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        count += 1

temp_fig['layout'].update(title='Temperature Plots', height=400*rowsn, showlegend=False, paper_bgcolor='#333f48', plot_bgcolor='#ffffff', titlefont={'color':'#ffffff'})

traces = []
n = len(sensor_list['PT and LC'])
rowsn= int(math.ceil(n/2.0))
PTLC_fig = tools.make_subplots(rows=rowsn, cols=2, subplot_titles=PTLC_titles)
titles=[]
for i in range(len(sensor_list['PT and LC'])):
    traces.append(go.Scatter(
        x=PTLC_time[i],
        y=PTLC_data[i],
        hoverinfo='y'
        ))
    titles.append(sensor_list['PT and LC'][i][0])
count = 0
for i in range(rowsn):
    for j in range(2):
        if count >= n:
            break
        PTLC_fig['layout']['annotations'][count]['font'].update(color='#ffffff')
        PTLC_fig.append_trace(traces[count], i+1, j+1)
        PTLC_fig['layout']['xaxis'+str(count + 1)].update(title='Time', showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2, range=[starttime, endtime])
        PTLC_fig['layout']['yaxis'+str(count + 1)].update(title=sensor_list['PT and LC'][count][3], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
        count += 1

PTLC_fig['layout'].update(title='Pressure Transducer and Load Cell Plots', height=400*rowsn, showlegend=False, paper_bgcolor='#333f48', plot_bgcolor='#ffffff', titlefont={'color':'#ffffff'})

#############################################################################################################################################################################################
#Create Dash object:
app = dash.Dash()
app.config['suppress_callback_exceptions']=True

#Add CSS and other external dash files
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
Logo = 'Logo.png'
encoded_image = base64.b64encode(open(Logo, 'rb').read())

#HTML layout
app.layout = html.Div(id='Page', children=[
    html.Header(className='row', style={'vertical-align':'middle'}, children=[
        html.Img(id='Logo', style={'width':'5%', 'height':'10%', 'float':'left'}, src='data:image/png;base64,{}'.format(encoded_image.decode())),
        html.Div(id='Title', style={'text-align':'center', 'float':'center'}, children=[
            html.H1(style={'color':'#333f48'}, children='Test Analysis and Run Program')
                ]),
        html.Div(id='SidebarToggle', children=[
            dcc.Dropdown(
                id='toggle-dropdown',
                options=[
                        {'label': 'Plots', 'value': 'Plots'},
                        {'label': 'Fill Calculator', 'value': 'FillCalc'},
                ],
                value='Plots'
                )
            ])
        ]),
    html.Main(id='Content'),
    # html.Div(className='Sidebar')
])

#############################################################################################################################################################################################
#Callbacks:
@app.callback(
    Output(component_id='Content', component_property='children'),
    [Input(component_id='toggle-dropdown', component_property='value')]
    )
def show_Content(input_value):
    if input_value=='Plots':
        return [html.Div(id='ContentHeader', style={'vertical-align':'middle'}, className='row', children=[
                html.Div(style={'float':'left', 'width':'20%'}, children=[
                    dcc.Dropdown(
                        id='plot-dropdown',
                        options=[
                            {'label': 'Temperature Plots', 'value': 'Temp'},
                            {'label': 'Transducer and Load Cell Plots', 'value': 'PTLC'},
                            {'label': 'All Plots', 'value': 'All'}
                        ],
                        value='Temp'
                    ),
                    ]),
                    html.Div(id='ContentTitle', style={'text-align':'center', 'float':'center'}, children=[
                        html.H2(style={'color':'#bf5700'}, children='Data')
                    ]),
                ]),
                # html.Div(id='Table', children=dcc.Graph(id='table', figure=table_fig)),
                html.Div(id='Plots', className='twelve columns', children=[dcc.Graph(id='DataTable', figure=table_fig), dcc.Graph(id='plots', figure=temp_fig)], style={'border': '6px solid #bf5700'})
            ]
    elif input_value=='FillCalc':
        return [html.Div(id='ContentHeader', style={'vertical-align':'middle'}, className='row', children=[
                html.Div(style={'float':'left', 'width':'20%'}, children=[
                    dcc.Input(id='tank-press', placeholder='Tank pressure (psi)', type='number', value=1),
                    dcc.Input(id='tank-weight', placeholder='Tank weight (lb)', type='number', value=1),
                    ]),
                    html.Div(id='ContentTitle', style={'text-align':'center', 'float':'center'}, children=[
                        html.H2(style={'color':'#bf5700'}, children='Fill Calculator')
                    ]),
                ]),
                # html.Div(id='Table', children=dcc.Graph(id='table', figure=table_fig)),
                html.Div(id='CalcOutput', className='twelve columns', style={'border': '6px solid #bf5700'})
            ]
    
@app.callback(
    Output(component_id='plots', component_property='figure'),
    [Input(component_id='plot-dropdown', component_property='value')]
    )
def update_Plots(input_value):
    if input_value=='Temp':
        return temp_fig
    if input_value=='PTLC':
        return PTLC_fig
    if input_value=='All':
        return all_fig

@app.callback(
    Output(component_id='CalcOutput', component_property='children'),
    [Input(component_id='tank-press', component_property='value'),
    Input(component_id='tank-weight', component_property='value')]
    )
def FillCalcTable(press, weight):
    press=float(press)
    weight=float(weight)
    print('Pressure: '+str(press))
    print('Weight: '+str(weight))
    volume=817.7*1.63871e-5
    press=press*6.8947572932 + 101.325
    weight=weight*0.453592
    pc=7251.0
    Tc=309.57
    rhoc=452.0
    #Find temperature
    b1=-6.71893
    b2=1.35966
    b3=-1.3779
    b4=-4.051
    def VapPress(Tr):
        return math.log((press/pc))-((1/Tr)*((b1*(1-Tr))+(b2*(1-Tr)**(3.0/2.0))+(b3*(1-Tr)**(5.0/2.0))+(b4*(1-Tr)**5.0)))

    Tr=optimize.fsolve(VapPress, 0.1,  xtol=10e-10)[0]
    T=Tr*Tc
    #Find liquid density
    b1=1.72328
    b2=-0.83950
    b3=0.51060
    b4=-0.10412
    liqdens = rhoc*math.exp((b1*((1-Tr)**(1.0/3.0)))+(b2*((1-Tr)**(2.0/3.0)))+(b3*(1-Tr))+(b4*((1-Tr)**(4.0/3.0))))
    #Find vapor density
    b1=-1.00900
    b2=-6.28792
    b3=7.50332
    b4=-7.90463
    b5=0.629427
    vapdens = rhoc*math.exp((b1*((1/Tr)-1)**(1.0/3.0))+(b2*((1/Tr)-1)**(2.0/3.0))+(b3*((1/Tr)-1))+(b4*((1/Tr)-1)**(4.0/3.0))+(b5*((1/Tr)-1)**(5.0/3.0)))
    #Find liqmass
    liqmass=(volume-(weight/vapdens))/((1.0/liqdens)-(1.0/vapdens))
    vapmass=(volume-(liqmass/liqdens))*vapdens
    ullage=((vapmass/vapdens)/volume)*100
    #unit change
    T=(T*1.8)-459.67
    liqmass=liqmass*2.20462262
    vapmass=vapmass*2.20462262
    fill_table_trace = go.Table(
        header=dict(values=['Tank Temperature (degF)', 'Amt. of Liquid (lb)', 'Amt. of Vapor (lb)', 'Ullage (%)'],
                    line = dict(color='#7D7F80'),
                    fill = dict(color='#a1c3d1'),
                    align = ['left'] * 5),
        cells=dict(values=[T, liqmass, vapmass, ullage],
                   line = dict(color='#7D7F80'),
                   fill = dict(color='#EDFAFF'),
                   align = ['left'] * 5))

    fill_table_layout = dict(width=1500, height=300)
    fill_table_data = [fill_table_trace]
    fill_table_fig = dict(data=fill_table_data, layout=fill_table_layout)
    return dcc.Graph(id='FillTable', figure=fill_table_fig)

#############################################################################################################################################################################################
#Run local host:
if __name__ == '__main__':
    app.run_server(debug=True)