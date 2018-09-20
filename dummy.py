# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
from dash.dependencies import Input, Output, State, Event
import plotly.graph_objs as go
import math
from plotly import tools
import numpy as np
from scipy import optimize
import serial
import os
import pandas as pd
from functions import SItoIPS, unitStr, Live_Table, FillCalcTable, makePlotsStatic, calibration, createPages, makePlotsLive
from sys import platform
import functools32
import logging
from collections import deque

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

#########################################################################################################
# Setup Serial
# if platform.startswith()
if platform.startswith('lin'):
    os.system('sudo chmod 666 /dev/ttyS3')
# ser = serial.Serial('/dev/ttyS3', 9600)

connected = False
ser = 0
# burntime = 10
OV4 = 0
OV5 = 0 
NV2 = 0
WV2 = 0
actuation = str(OV4) + ' ' + str(OV5) + ' ' + str(NV2) + ' ' + str(WV2) 
# data = np.array([5, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1])

#########################################################################################################
# Import sensor data

with open('sensor_data/sensor_input.txt') as sensorcsv:
    sensordict = pd.read_csv(sensorcsv, delimiter='\t')

data_header = pd.Series('Time').append(sensordict.Abv, ignore_index=True)
livedata = pd.DataFrame(columns=data_header)

deque_list = {'Time': deque(maxlen=10)}
for sensor in sensordict['Abv']:
    deque_list[sensor] = deque(maxlen=10)

#############################################################################################################################################################################################
#Create Dash object:
app = dash.Dash()
app.config['suppress_callback_exceptions']=True

#Add CSS and other external dash files
Logo = 'Logo.png'
encoded_image = base64.b64encode(open(Logo, 'rb').read())

#HTML layout
app.layout = html.Header(id='Page', children=[
    dcc.Interval(
        id='update',
        interval=1000,
        n_intervals=0
        ),
    html.Div(className='row', style={'vertical-align':'middle'}, children=[
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
                        {'label': 'SI/', 'value': 'SI'},
                        {'label': 'IPS', 'value': 'IPS'},
                ],
                value='SI'
                ),
            html.Button('Live', id='live-toggle', n_clicks=0),
            dcc.Input(id='input-port', placeholder='Channel', type='number', value=0),
            html.H3(id='channel-id'),
            dcc.RadioItems(
                id='read-write',
                options=[
                        {'label': 'Read/', 'value': 'r'},
                        {'label': 'Write', 'value': 'w'},
                ],
                value='r'
                ),
            dcc.Input(id='file-id', placeholder='File', type='string'),
        ]),
    html.Main(id='live-content'),
    html.Main(id='static-content'),
    ])
])

#############################################################################################################################################################################################
#Callbacks:
@functools32.lru_cache(maxsize=32)
@app.callback(
    Output(component_id='channel-id', component_property='children'),
    [Input(component_id='input-port', component_property='value'),
    Input(component_id='live-toggle', component_property='n_clicks')]
    )
def set_Channel(port, n_clicks):
    global connected
    global ser
    print(port, n_clicks)
    if port != 0 and n_clicks%2 != 0:
        port = str(port)
        if platform.startswith('lin'):
            print('Connecting to serial port')
            try:
                ser = serial.Serial('/dev/ttyS'+port, 9600)
                connected = True
                print('Connected on port: ' + port)
                return 'Connected on port: /dev/ttyS' + port
            except:
                print('Serial port not found')
                return 'Error with serial connection'
        elif platform.startswith('win'):
            print('Connecting to serial port')
            try:
                ser = serial.Serial('COM'+port, 9600)
                connected = True
                print('Connected on port: ' + port)
                return 'Connected on port: COM' + port
            except:
                print('Serial port not found')
                return 'Error with serial connection'
    elif port == 0 or n_clicks%2 == 0:
        print('Not connected')
        port = str(port)
        connected = False 
        return 'No live data connection'

@app.callback(
    Output(component_id='live-content', component_property='children'),
    [Input(component_id='change-page', component_property='value'),
    Input(component_id='toggle-units', component_property='value'),
    Input(component_id='read-write', component_property='value'),
    Input(component_id='file-id', component_property='value')],
    events=[Event('update', 'interval')]
    )
def update_Data(page, unit, rw, file):
    global connected
    global ser
    global livedata
    global actuation
    if connected == True:
        if ser.inWaiting() > 0:
            new = ser.readline()
            new = new.split(',')
            new = [float(i) for i in new]
            print(len(data_header))
            print(len(new))
            for i in range(len(new)-1):
                new[i] = new[i]*sensordict['a'][i] + sensordict['b'][i]
            livedata.loc[len(livedata)] = new
            ser.reset_output_buffer()
            burntime = 10
            ser.write(actuation)
            print(actuation)
            if len(livedata['Time'])%10 == 0 and rw == 'w':
                print('Writing')
                livedata.to_csv('data/'+file+'.txt', sep='\t')
                sensordict.to_csv('sensor_data/'+file+'_sensor_input.txt', sep='\t')
            # if len(livedata) > 10:
            #     plotdata = livedata.tail(10)
            deque_list['Time'].append(new[0])
            for i in range(len(new)-1)[1:]:
                deque_list[sensordict['Abv'][i]].append(new[i])
            # print(deque_list)
            # try:
            #     return createPages(connected, sensordict, livedata, unit, page, burntime, deque_list)
            # except:
            #     return 'Loading data'
            return createPages(connected, sensordict, livedata, unit, page, burntime, deque_list)

@functools32.lru_cache(maxsize=32)
@app.callback(
    Output(component_id='static-content', component_property='children'),
    [Input(component_id='change-page', component_property='value'),
    Input(component_id='toggle-units', component_property='value'),
    Input(component_id='read-write', component_property='value'),
    Input(component_id='file-id', component_property='value')]
    )
def static_Data(page, unit, rw, file):
    global connected
    global burntime
    if connected == False and rw == 'r':
        try:
            with open('sensor_data/'+file + '_sensor_input.txt') as sensorcsv:
                sensordict = pd.read_csv(sensorcsv, delimiter='\t')
            staticdata = pd.read_csv('data/'+file + '.txt', sep='\t')
            for i in range(len(staticdata['LC5']))[1:]:
                if abs(staticdata['LC5'][i]) - abs(staticdata['LC5'][i-1]) > 40:
                    starttime = staticdata['Time'][i]
                elif abs(staticdata['LC5'][i]) - abs(staticdata['LC5'][i-1]) < -40:
                    endtime = staticdata['Time'][i]
            for i in range(len(staticdata['Time'])):
                staticdata['Time'][i] -= starttime
            burntime = endtime - starttime
            new_page = createPages(connected, sensordict, staticdata, unit, page, burntime, staticdata)
            return new_page
        except:
            return 'Please enter valid filename'

@functools32.lru_cache(maxsize=32)
@app.callback(
    Output(component_id='act-string', component_property='children'),
    [Input(component_id='change-page', component_property='value'),
    Input(component_id='OV4', component_property='n_clicks'),
    Input(component_id='OV5', component_property='n_clicks'),
    Input(component_id='NV2', component_property='n_clicks'),
    Input(component_id='WV2', component_property='n_clicks')]
    )
def changeActuation(page, OV4_click, OV5_click, NV2_click, WV2_click):
    global connected
    global OV4
    global OV5 
    global NV2
    global WV2
    global actuation
    if connected==True and page == 'PID':
        if OV4_click != 0:
            OV4 += 1
        if OV5_click != 0:
            OV5 += 1
        if NV2_click != 0:
            NV2 += 1
        if WV2_click != 0:
            WV2 += 1

        if OV4%2 == 0:
            OV4_act = 0
        else:
            OV4_act = 1
        if OV5%2 == 0:
            OV5_act = 0
        else:
            OV5_act = 1
        if NV2%2 == 0:
            NV2_act = 0
        else:
            NV2_act = 1
        if WV2%2 == 0:
            WV2_act = 0
        else:
            WV2_act = 1
        actuation = str(OV4_act) + ' ' + str(OV5_act) + ' ' + str(NV2_act) + ' ' + str(WV2_act)
        return actuation

# @app.callback(Output(component_id='click-message', component_property='children'),
#               [Input(component_id='write-csv', component_property='n_clicks')],
#               [State(component_id='Channel', component_property='value'),
#                State(component_id='Class', component_property='value'),
#                State(component_id='Name', component_property='value'),
#                State(component_id='Abv', component_property='value'),
#                State(component_id='SIunit', component_property='value'),
#                State(component_id='a', component_property='value'),
#                State(component_id='b', component_property='value')]
#                )
# def update_CSV(n_clicks, Channel, Class, Name, Abv, SIunit, a, b):
#     # df = pd.DataFrame(np.array([Class, Name, Abv, Channel, SIunit, a, b]))
#     print('button clicked')
#     if (Abv in sensordict.Abv.values) == True:
#         sensordict.loc[np.where(sensordict.Abv.values==Abv)[0][0],'Class':'b'] = Class, Name, Abv, Channel, SIunit, a, b
#         print(Class, Name, Abv, Channel, SIunit, a, b)
#         sensordict.to_csv('sensor_input.csv')
#         print(sensordict)
#         return 'Updated CSV'
#     elif (Abv in sensordict.Abv.values) == False:
#         df = pd.DataFrame(np.array([Class, Name, Abv, Channel, SIunit, a, b]))
#         print(Class, Name, Abv, Channel, SIunit, a, b)
#         sensordict.append(df)
#         sensordict.to_csv('sensor_input.csv')
#         print(sensordict)
#         return 'Added to CSV'

    
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
for js in external_css:
    app.scripts.append_script({'external_url': js})

#############################################################################################################################################################################################
#Run local host:
if __name__ == '__main__':
    app.server.run(port=8150, host='127.0.0.1', debug=True)
    # app.run_server(debug=False)