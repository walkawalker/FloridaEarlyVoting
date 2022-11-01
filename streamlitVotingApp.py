# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:36:58 2022

@author: whill
"""

import streamlit as st
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import plotly.express as px
import plotly.figure_factory as ff

def counties():
   df_counties = pd.read_csv('masterfips.csv')
   return df_counties
def florida(dfc):
    dfflorida = dfc[dfc['STNAME']=='Florida']
    florida = "https://countyballotfiles.floridados.gov/VoteByMailEarlyVotingReports/PublicStats"
    flurl = requests.get(florida)
    flsoup = BeautifulSoup(flurl.content, "html.parser")
    flres = flsoup.find(id="countyTotal")
    table= flres.find_all('table')
    dfNYR=pd.read_html(str(table[0]))[0]
    dfVBM=pd.read_html(str(table[1]))[0]
    dfVE=pd.read_html(str(table[2]))[0]
    #dfNYR.join(dfflorida)
    dfNYR['Fips']=dfflorida['FIPS'].tolist()
    dfVBM['Fips']=dfflorida['FIPS'].tolist()
    dfVE['Fips']=dfflorida['FIPS'].tolist()
    dfVE['Compiled'] = dfVE['Compiled'].fillna(0)
    return dfNYR, dfVBM, dfVE
def makemapplot(df, party, check_flag):
    values = df[party].tolist()
    fips = df['Fips'].tolist()
    if check_flag:
        endpts = list(np.mgrid[min(values):max(values):4j])
    else:
        endpts = list(np.mgrid[1:max(values):4j]) 
    colorscale = ["#030512","#1d1d3b","#323268","#3d4b94","#3e6ab0",
              "#4989bc","#60a7c7","#85c5d3","#b7e0e4","#eafcfd"]
    fig = ff.create_choropleth(
        fips=fips, values=values, scope=['Florida'], show_state_data=True,
        colorscale=colorscale, binning_endpoints=endpts, round_legend_values=True,
        plot_bgcolor='rgb(229,229,229)',
        paper_bgcolor='rgb(229,229,229)',
        legend_title='Count by County',
        county_outline={'color': 'rgb(255,255,255)', 'width': 0.5},
        exponent_format=True
    )
    fig.update_layout(height=700, margin={"r":0,"t":0,"l":0,"b":0})
    hover_ix, hover = [(ix, t) for ix, t in enumerate(fig['data']) if t.text][0]
    # mismatching lengths indicates bug
    if len(hover['text']) != len(df):
    
        ht = pd.Series(hover['text'])
    
        no_dupe_ix = ht.index[~ht.duplicated()]
    
        hover_x_deduped = np.array(hover['x'])[no_dupe_ix]
        hover_y_deduped = np.array(hover['y'])[no_dupe_ix]
    
        new_hover_x = [x if type(x) == float else x[0] for x in hover_x_deduped]
        new_hover_y = [y if type(y) == float else y[0] for y in hover_y_deduped]
    
        fig['data'][hover_ix]['text'] = ht.drop_duplicates()
        fig['data'][hover_ix]['x'] = new_hover_x
        fig['data'][hover_ix]['y'] = new_hover_y
    fig.layout.template = None
    return fig
def makebarplot(df,party, strval):
    bardf = df.nlargest(10, party)
    fig = px.bar(bardf, x='County', y=party, title=f'Top 10 Counties for {party} {strval}')
    fig.update_layout(title_x=0.5)
    return fig
if __name__ == "__main__":
    dfc = counties()
    df1, df2, df3 = florida(dfc)
    st.set_page_config(page_title = 'Early Voting Dashboard', layout = 'wide')
    st.title('Midterm Elections 2022: Florida Early Voting Dashboard')
    st.text('The data was last updated at: ' + df1['Compiled'][0])
    with st.container():
        party = st.radio("Breakdown by party", ('Republican', 'Democrat','Other','No Party Affiliation', 'Total'))
    tab1, tab2, tab3 = st.tabs(["Mail Ballots Not Yet Returned", "Voted Vote-By-Mail", "Voted Early"])
    with tab1:
        st.plotly_chart(makemapplot(df1, party, check_flag=True), use_container_width=True)
        st.plotly_chart(makebarplot(df1, party, strval= 'Outstanding Mail Ballots'),use_container_width=True)
    with tab2:
        st.plotly_chart(makemapplot(df2, party, check_flag=True), use_container_width=True)
        st.plotly_chart(makebarplot(df2, party, strval= 'Returned Mail Ballots'),use_container_width=True)
    with tab3:
        st.plotly_chart(makemapplot(df3, party, check_flag=False), use_container_width=True)
        st.plotly_chart(makebarplot(df3, party, strval= 'Early Voters'),use_container_width=True)
    
        