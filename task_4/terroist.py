import random
import textwrap
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('globalterrorismdb_0718dist.csv', low_memory=False, usecols=['iyear', 'imonth', 'iday', 'country_txt', 'city', 
                                                                              'longitude', 'latitude', 'nkill', 'nwound', 
                                                                              'summary', 'target1', 'gname', 'attacktype1_txt', 'region_txt'])
df.rename(columns={'iyear':'year', 'imonth':'month', 'iday':'day', 'country_txt':'country', 'city':'city', 'longitude':'longitude', 
                   'latitude':'latitude', 'nkill':'killed', 'nwound':'wounded', 'summary':'summary', 'target1':'target', 
                   'gname':'group_name', 'attacktype1_txt':'attack_type', 'region_txt':'region'}, inplace=True)
# removing rows with month=0
df = df[df['month']!=0]

# removing rows with day = 0
df = df[df.day!=0]

# creating a date column
df['date'] = [dt.datetime(y,m,d) for y, m, d in zip(df['year'], df['month'], df['day'])]

# creating dashboard
app = dash.Dash()
server = app.server
app.title = 'Global Terrorist Attack Data Visualization Dashboard'


# app layout
app.layout = html.Div([
    dcc.Graph(id='map', config={'displayModeBar': False}),

    html.Div([
        dcc.RangeSlider(id='years_1',
                        min=df.year.min(),
                        max=df.year.max(),
                        dots=True,
                        value=[2010, df.year.max()],
                        marks={str(yr): "'" + str(yr)[2:] for yr in range(df.year.min(), df.year.max()+1)}),
         
        html.Br(),
        html.Br()
    ], style={'width':'80%', 'margin-left':'10%', 'background-color':'#f2f2f2'}),
    html.Div([
        dcc.Dropdown(id='countries',
                     multi=True,
                     value=[''],
                     placeholder='Select Countries from here',
                     options=[{'label':i, 'value':i} for i in sorted(df['country'].unique())]),
        html.Br(),
        html.Br()
    ], style={'width':'60%', 'margin-left':'20%', 'background-color':'#f2f2f2'}),
    
    dcc.Graph(id='country_by_year', config={'displayModeBar':False}),
    html.Hr(), 
#     html.Content('Top Countries', style={'font-family':'Palatino', 'margin-left':'45%', 'font-size':25}),
    html.Br(),

    html.Div([
        html.Div([
            html.Div([
                dcc.RangeSlider(id='years_2',
                                min=df.year.min(),
                                max=df.year.max(),
                                dots=True,
                                value=[2012, df.year.max()],
                                marks={str(y): str(y) for y in range(df.year.min(), df.year.max()+1, 5)}),
                html.Br(),                
            ], style={'margin-left':'8%', 'margin-right':'1%'}),
            dcc.Graph(id='country_attacks', config={'displayModeBar':False}, figure={'layout':{'margin':{'r':10, 't':50}}}),
            html.Hr(),
            html.Br(),
            dcc.Graph(id='deaths', config={'displayModeBar':False}, figure={'layout':{'margin':{'r':10, 't':50}}})
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.Div([
                dcc.RangeSlider(id='years_3',
                                min=df.year.min(),
                                max=df.year.max(),
                                dots=True,
                                value=[2010, df.year.max()],
                                marks={str(yr): str(yr) for yr in range(df.year.min(), df.year.max()+1, 5)}),
                html.Br(),
                
            ], style={'margin-left':'1%', 'margin-right':'3%'}),

            dcc.Graph(id='country_deaths', config={'displayModeBar':False}, figure={'layout':{'margin':{'l':10, 't':50}}}),
            html.Hr(),
            html.Br(),
            dcc.Graph(id='g_name', config={'displayModeBar':False}, figure={'layout':{'margin':{'l':10, 't':50}}}),
        ], style={'width':'48%', 'display':'inline-block', 'float':'right'}),
    ]),
    
    html.P(),
    html.Content('Global Terrorism Data from 1970 till 2017')    
], style={'background-color': '#e9e2e2e'})


# first callback
@app.callback(Output('country_by_year', 'figure'),
             [Input('countries', 'value'), Input('years_1', 'value')])
def countryBarchatYear(countries, years):
    df_cpy = df[df['country'].isin(countries) & df['year'].between(years[0], years[1])]
    df_cpy = df_cpy.groupby(['year', 'country'], as_index=False)['date'].count()
    
    return {
        'data': [go.Bar(x=df_cpy[df_cpy['country'] == i]['year'],
                        y=df_cpy[df_cpy['country'] == i]['date'], name=i) for i in countries] ,
        'layout': go.Layout(title='Yearly Terrorist Attacks ' + ', '.join(countries) + '  ' + ' - '.join([str(y) for y in years]),
                            plot_bgcolor='#f2f2f2',
                            paper_bgcolor='#f2f2f2',
                            font={'family': 'Baskerville'},
                            titlefont={'size': 24})
    }


# second callback
@app.callback(Output('map', 'figure'),
        [Input('countries', 'value'), Input('years_1', 'value')])


def CountryOnMap(countries, years):
    df_com = df[df['country'].isin(countries) & df['year'].between(years[0], years[1])]
    
    return {
        'data': [go.Scattergeo(lon=[x + random.gauss(0.04, 0.03) for x in df_com[df_com['country'] == i]['longitude']],
                               lat=[x + random.gauss(0.04, 0.03) for x in df_com[df_com['country'] == i]['latitude']],
                               name=i,
                               hoverinfo='text',
                               opacity=0.9,
                               marker={'size':9, 'line':{'width':0.2, 'color':'#cccccc'}},
                               hovertext= df_com[df_com.country==i].city.astype(str) + ', ' + df_com[df_com.country==i].country.astype(str) + '<br>' + 
                                            [dt.datetime.strftime(d, '%d %B %Y') for d in df_com[df_com.country==i].date] + '<br>' + 
                                            'Perpetrator: ' + df_com[df_com.country==i].group_name.astype(str) + '<br>' + 
                                            'Killed: ' + df_com[df_com.country==i].killed.astype(str) + '<br>' + 
                                            'Wounded: ' + df_com[df_com.country==i].wounded.astype(str) + '<br>' + 
                                            'Target: ' + df_com[df_com.country==i].target.astype(str) + '<br>' + 
                                            ['<br>'.join(textwrap.wrap(x, 40)) if not isinstance(x, float) else "" for x in df_com[df_com.country==i].summary])
                        for i in countries],
        
        'layout': go.Layout(title='Terrorist Attacks ' + ', '.join(countries) + '  ' + ' - '.join([str(y) for y in years]),
                            font={'family': 'Baskerville'},
                            titlefont={'size': 24},
                            paper_bgcolor='#f2f2f2',
                            plot_bgcolor='#f2f2f2',
                            width=1420,
                            height=650,
                            geo={'showland': True, 'landcolor': '#f2f2f2',
                                 'countrycolor': '#bebebe',
                                 'showsubunits': True,
                                 'subunitcolor': '#bebebe',
                                 'subunitwidth': 5,
                                 'showcountries': True,
                                 'oceancolor': '#a8e6ff',
                                 'showocean': True,
                                 'showcoastlines': True, 
                                 'showframe': False,
                                 'coastlinecolor': '#006994',
                                 'lonaxis': {'range': [df_com.longitude.min()-1, df_com.longitude.max()+1]},
                                 'lataxis': {'range': [df_com.latitude.min()-1, df_com.latitude.max()+1]}
                                              })
    }


#third callback
@app.callback(Output('country_attacks', 'figure'),
        [Input('countries', 'value') ,Input('years_2', 'value')])

def active_terrorist_group(countries, years):
    df_atg = df[df['country'].isin(countries) & df['year'].between(years[0], years[1])]
    df_atg = df_atg.groupby(['country', 'group_name'], as_index=False)['date'].count().sort_values('date', ascending=False)#[:20]
    
    return {
        'data': [go.Bar(x=df_atg[df_atg.country == i].group_name[:5],
                        y=df_atg[df_atg.country == i].date[:5], name=i) for i in countries],
        'layout': go.Layout(title='Top 5 Active Terrorist Group in ' + ', '.join(countries) + '  ' + ' - '.join([str(y) for y in years]),
                            plot_bgcolor='#f2f2f2',
                            paper_bgcolor='#f2f2f2',
                            font={'family': 'Baskerville'},
                            titlefont={'size': 24})
    }


# fourth callback
@app.callback(Output('country_deaths', 'figure'),
        [Input('countries', 'value'), Input('years_3', 'value')])

def active_group_target_places(countries, years):
    df_tp = df[df['country'].isin(countries) & df['year'].between(years[0], years[1])]
    df_tp = df_tp.groupby(['country', 'target'], as_index=False)['date'].count().sort_values('date', ascending=False)
    
    return {
        'data': [go.Bar(x=df_tp[df_tp.country == i].target[:5],
                        y=df_tp[df_tp.country == i].date[:5], 
                        name=i) for i in countries],
        'layout': go.Layout(title='Top 5 Targets by Terrorist Groups in ' + ', '.join(countries) + '  ' + ' - '.join([str(y) for y in years]),
                            plot_bgcolor='#f2f2f2',
                            paper_bgcolor='#f2f2f2',
                            font={'family': 'Baskerville'},
                            titlefont={'size': 24})
    }


# fifth callback
@app.callback(Output('g_name', 'figure'),
        Input('years_3', 'value'))

def countries_attacked(years):
    df_gn = df[df.year.between(years[0], years[1])]
    df_gn = df_gn.groupby('group_name', as_index=False).date.count().sort_values('date', ascending=False)
    
    return {
        'data': [go.Bar(x=df_gn['date'][:15],
                        y=df_gn.group_name[:15],
                        showlegend=False,
                        constraintext='none',
                        orientation='h',
                        text=df_gn.group_name[:15],
                        textposition='outside')],
        'layout': go.Layout(title='Most Active Terrorist Groups during' + ' ' + ' - '.join([str(y) for y in years]),
                            plot_bgcolor='#f2f2f2',
                            paper_bgcolor='#f2f2f2',
                            font={'family': 'Baskerville'},
                            titlefont={'size': 24},
                            yaxis={'visible': False})
    }


# sixth callback
@app.callback(Output('deaths', 'figure'),
        Input('years_2', 'value'))

def countries_attacked(years):
    df_wd = df[df.year.between(years[0], years[1])]
    df_wd = df_wd.groupby('country', as_index=False).killed.agg(['sum', 'count']).sort_values('sum', ascending=False)
    
    return {
        'data': [go.Bar(x=df_wd['sum'][:15],
                        y=df_wd.index[:15],
                        showlegend=False,
                        constraintext='none',
                        orientation='h',
                        text=df_wd.index[:15],
                        textposition='outside')],
        'layout': go.Layout(title='Top 15 Countries by Deaths during' + ' ' + ' - '.join([str(y) for y in years]),
                            plot_bgcolor='#f2f2f2',
                            paper_bgcolor='#f2f2f2',
                            font={'family': 'Baskerville'},
                            titlefont={'size': 24},
                            yaxis={'visible': False})
    }


if __name__ == '__main__':
    app.run_server()