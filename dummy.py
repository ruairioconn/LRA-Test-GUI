# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import math
from plotly import tools
import numpy as np
from scipy import optimize
import serial
import os
import pandas as pd
from functions import SItoIPS, unitStr, Live_Table, FillCalcTable, makePlots, calibration

#########################################################################################################
# Setup Serial
os.system('sudo chmod 666 /dev/ttyS3')
ser = serial.Serial('/dev/ttyS3', 9600)

# data = np.array([5, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1])
data = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

#########################################################################################################
# Import sensor data

with open('sensor_input.txt') as sensorcsv:
    sensordict = pd.read_csv(sensorcsv, delimiter='\t')

#############################################################################################################################################################################################
#Create Dash object:
app = dash.Dash()
app.config['suppress_callback_exceptions']=True

#Add CSS and other external dash files
Logo = 'Logo.png'
encoded_image = base64.b64encode(open(Logo, 'rb').read())

#HTML layout
app.layout = html.Div(id='Page', children=[
    dcc.Interval(
        id='update',
        interval=50,
        n_intervals=0
        ),
    html.Header(className='row', style={'vertical-align':'middle'}, children=[
        html.Img(id='Logo', style={'width':'5%', 'height':'10%', 'float':'left'}, src='data:image/png;base64,{}'.format(encoded_image.decode())),
        html.Div(id='Title', style={'text-align':'center', 'float':'center'}, children=[
            html.H1(style={'color':'#333f48'}, children='Test Analysis and Run Program')
                ]),
        html.Div(id='SidebarToggle', children=[
            dcc.Dropdown(
                id='change-page',
                options=[
                        {'label': 'Plots', 'value': 'Plots'},
                        {'label': 'Fill Calculator', 'value': 'FillCalc'},
                        {'label': 'Calibration', 'value': 'Calibration'},
                        {'label': 'Diagram', 'value': 'PID'},
                ],
                value='PID'
                ),
            dcc.RadioItems(
                id='toggle-units',
                options=[
                        {'label': 'SI', 'value': 'SI'},
                        {'label': 'IPS', 'value': 'IPS'},
                ],
                value='SI'
                ),
            html.Button('Live', id='live-toggle'),
            # html.Input(id='input-port', )
        ]),
    html.Main(id='Content'),
    ])
])

#############################################################################################################################################################################################
#Callbacks:
@app.callback(
    Output(component_id='Content', component_property='children'),
    [Input(component_id='change-page', component_property='value'),
    Input(component_id='toggle-units', component_property='value'),
    Input(component_id='live-toggle', component_property='n_clicks'),
    Input(component_id='update', component_property='n_intervals')]
    )
def update_Data(page, unit, n_clicks, n_ints):
    if ser.inWaiting()>0:
        new = ser.readline()
        new = new.split()
        new = [float(i) for i in new]
        for i in range(len(new)-1):
            new[i] = new[i]*sensordict['a'][i] + sensordict['b'][i]
        data.append(new)
        #Create live readout
        if page == 'PID':
            live_table = Live_Table(sensordict, data, unit)
            return live_table
        elif page == 'FillCalc':
            press = data[len(data)-1][sensordict['Channel'][np.where(sensordict['Name']=='Tank Pressure')[0][0]]]
            weight = data[len(data)-1][sensordict['Channel'][np.where(sensordict['Name']=='Accumulator Scale')[0][0]]]
            fill_table = FillCalcTable(press, weight, unit)
            return fill_table
        elif page == 'Calibration':
            content = calibration(sensordict)
            return content
        # elif page == 'Plots':
        #     graph = makePlots(sensordict, data, unit)
        #     return graph

@app.callback(Output(component_id='click-message', component_property='children'),
              [Input(component_id='write-csv', component_property='n_clicks')],
              [State(component_id='Channel', component_property='value'),
               State(component_id='Class', component_property='value'),
               State(component_id='Name', component_property='value'),
               State(component_id='Abv', component_property='value'),
               State(component_id='SIunit', component_property='value'),
               State(component_id='a', component_property='value'),
               State(component_id='b', component_property='value')]
               )
def update_CSV(n_clicks, Channel, Class, Name, Abv, SIunit, a, b):
    # df = pd.DataFrame(np.array([Class, Name, Abv, Channel, SIunit, a, b]))
    print('button clicked')
    if (Abv in sensordict.Abv.values) == True:
        sensordict.loc[np.where(sensordict.Abv.values==Abv)[0][0],'Class':'b'] = Class, Name, Abv, Channel, SIunit, a, b
        print(Class, Name, Abv, Channel, SIunit, a, b)
        sensordict.to_csv('sensor_input.csv')
        print('Wrote to CSV')
        return 'Updated CSV'
    elif (Abv in sensordict.Abv.values) == False:
        df = pd.DataFrame(np.array([Class, Name, Abv, Channel, SIunit, a, b]))
        print(Class, Name, Abv, Channel, SIunit, a, b)
        sensordict.append(df)
        sensordict.to_csv('sensor_input.csv')
        print('Wrote to CSV')
        return 'Added to CSV'

    


#############################################################################################################################################################################################
#Run local host:
if __name__ == '__main__':
    app.run_server(debug=True)