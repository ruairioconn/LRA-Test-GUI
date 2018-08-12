import numpy as np
import math
import plotly.graph_objs as go
import dash_core_components as dcc
from scipy import optimize
from plotly import tools
import dash_html_components as html

def SItoIPS(data, unit):
	''' Takes in a list of data and it's corresponding unit and return the converted list '''
	if unit == 'kg':
		''' kg to lb '''
		converted_data = data * 2.20462
		return converted_data
	if unit == 'kPa':
		''' kPa to psi '''
		converted_data = data * 0.145038
		return converted_data
	if unit == 'kg/s':
		''' kg/s to lb/s '''
		converted_data = data * 2.20462
		return converted_data
	if unit == 'N':
		''' N to lbf '''
		converted_data = data * 0.224809
		return converted_data
	if unit == 'Ns':
		''' Ns to lbfs '''
		converted_data = data * 0.224809
		return converted_data
	if unit == 'degC':
		'''degC to degF '''
		converted_data = ((data * 9.0/5.0)+32) 
		return converted_data

def unitStr(unit):
	''' Takes in SI unit and returns IPS equivalent '''
	if unit == 'kg':
		''' kg to lb '''
		return 'lb'
	if unit == 'kPa':
		''' kPa to psi '''
		return 'psi'
	if unit == 'kg/s':
		''' kg/s to lb/s '''
		return 'lb/s'
	if unit == 'N':
		''' N to lbf '''
		return 'lbf'
	if unit == 'Ns':
		''' Ns to lbfs '''
		return 'lbfs'
	if unit == 'degC':
		'''degC to degF '''
		return 'degF'

def FillCalcTable(press, weight, unit):
    press=float(press)
    weight=float(weight)
    volume=817.7*1.63871e-5
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
    T = T-273.15
    header=dict(values=['Tank Temperature (degC)', 'Amt. of Liquid (kg)', 'Amt. of Vapor (kg)', 'Ullage (%)'], line = dict(color='#7D7F80'), fill = dict(color='#a1c3d1'), align = ['left'] * 5)
    #unit change
    if unit == 'IPS':
	    T=(T*1.8)+32
	    liqmass=liqmass*2.20462262
	    vapmass=vapmass*2.20462262
	    header=dict(values=['Tank Temperature (degF)', 'Amt. of Liquid (lb)', 'Amt. of Vapor (lb)', 'Ullage (%)'],
	            line = dict(color='#7D7F80'),
	            fill = dict(color='#a1c3d1'),
	            align = ['left'] * 5)
    fill_table_trace = go.Table(header=header,
        cells=dict(values=[T, liqmass, vapmass, ullage],
                   line = dict(color='#7D7F80'),
                   fill = dict(color='#EDFAFF'),
                   align = ['left'] * 5))

    fill_table_data = [fill_table_trace]
    fill_table_fig = dict(data=fill_table_data)
    return dcc.Graph(id='FillTable', figure=fill_table_fig)


def Live_Table(sensordict, data, unit):
	values = []
	header = []
	for i in range(len(sensordict)):
		name = sensordict['Name'][i]
		u = sensordict['SIunit'][i]
		value = data[len(data)-1][sensordict['Channel'][i]]
		if unit == 'IPS':
		    value = SItoIPS(value, u)
		    u = unitStr(u)
		s = str(value) + '\n (' + u + ')'
		values.append(s)
		header.append(name)
	cells = dict(values=values)
	header = dict(values=header)
	trace = go.Table(header=header, cells=cells)
	fig = dict(data=[trace])
	return dcc.Graph(id='live-data-table', figure=fig)       

def makePlots(sensordict, data, unit):
	traces = []
	n = len(sensordict)
	rowsn= int(math.ceil(n/2.0))
	fig = tools.make_subplots(rows=rowsn, cols=2, subplot_titles=sensordict['Name'])
	titles=[]
	if unit == 'SI':
		for i in range(len(sensordict)):
		    traces.append(go.Scatter(
		        x=[row[0] for row in data],
		        y=[row[sensordict['Channel'][i]] for row in data],
		        hoverinfo='y'
		    ))
		    titles.append(sensordict['Name'][i])
	# print(titles)
	elif unit == 'IPS':
		for i in range(len(sensordict)):
		    traces.append(go.Scatter(
		        x=[row[0] for row in data],
		        y=[SItoIPS(row[sensordict['Channel'][i]], sensordict['SIunit'][i]) for row in data],
		        hoverinfo='y'
		    ))
		    titles.append(sensordict['Name'][i])
	count = 0
	print(titles)
	for i in range(rowsn):
	    for j in range(2):
	        if count >= n:
	            break
	        temp_fig['layout']['annotations'][count]['font'].update(color='#ffffff')
	        temp_fig.append_trace(traces[count], i+1, j+1)
	        temp_fig['layout']['xaxis'+str(count + 1)].update(title='Time', showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
	        temp_fig['layout']['yaxis'+str(count + 1)].update(title=sensordict['SIunit'][count], showline=True, mirror=True, showgrid=True, color='#ffffff', linecolor='#bf5700', linewidth=3, gridcolor='#333f48', zerolinecolor='#bf5700', zerolinewidth=2)
	        if unit == 'IPS':
	        	u = unitStr(sensordict['SIunit'][count])
	        	temp_fig['layout']['yaxis'+str(count + 1)].update(title=u)
	        count += 1

	fig['layout'].update(title='Temperature Plots', height=400*rowsn, showlegend=False, paper_bgcolor='#333f48', plot_bgcolor='#ffffff', titlefont={'color':'#ffffff'})   
	return dcc.Graph(id='plots', figure=fig)

def calibration(sensordict):
	content = html.Div(children=[
		html.H2(id='click-message', children=[]),
		html.Div(children=[html.H3('Channel: '), dcc.Input(id='Channel', placeholder='Channel', type='number')]),
		html.Div(className='row', children=[
			html.Div(className='one-half column', children = [
			html.H3('Class: '), dcc.Input(id='Class', placeholder='Class', type='string'),
			html.H3('Name: '), dcc.Input(id='Name', placeholder='Name', type='string'),
			html.H3('Abv: '), dcc.Input(id='Abv', placeholder='Abv', type='string')
			]),
		html.Div(className='one-half column', children = [
			html.H3('SI unit: '), dcc.Input(id='SIunit', placeholder='SIunit', type='string'),
			html.H3('a: '), dcc.Input(id='a', placeholder='a', type='number'),
			html.H3('b: '), dcc.Input(id='b', placeholder='b', type='number')
			])
			]),
		html.Button('Write to CSV', id='write-csv')
		])
	return content