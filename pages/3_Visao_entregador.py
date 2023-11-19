import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine, Unit
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregador', layout='wide')

df = pd.read_csv(r"dataset/train.csv", skipinitialspace=True)

df1 = df.copy()

def avali_porentregador(df1):
    cols = ['Delivery_person_ID', 'Delivery_person_Ratings']
    avaliacao_media_entregador = (df1.loc[:, cols]
                                    .groupby('Delivery_person_ID')
                                    .mean().reset_index())
    return avaliacao_media_entregador

def avali_portransito(df1):
    media_tipodetrafego = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                            .groupby('Road_traffic_density')
                            .agg({'Delivery_person_Ratings': ['mean', 'std']}))
    media_tipodetrafego.columns = ['Delivery_mean', 'Delivery_std']
    media_tipodetrafego = media_tipodetrafego.reset_index()
    return media_tipodetrafego

def avali_porclima(df1):
    media_std_condicao = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                .groupby('Weatherconditions')
                                .agg({'Delivery_person_Ratings': ['mean', 'std']}))
    media_std_condicao.columns = ['Delivery_mean', 'Delivery_std']
    media_std_condicao = media_std_condicao.reset_index()
    return media_std_condicao

def ordenar_entregador(df1, ordenacao):
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                    .groupby(['City', 'Delivery_person_ID'])
                    .min().sort_values(['City', 'Time_taken(min)'],
                    ascending=ordenacao).reset_index())
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban'].head(10)
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3
def media_entrega_clima(df1):
    cols = ['Time_taken(min)', 'Weatherconditions']
    df1_aux = df1.loc[:, cols].groupby('Weatherconditions').mean().reset_index()
    fig = (px.bar(df1_aux, x='Weatherconditions', y='Time_taken(min)'
            , labels= {'Weatherconditions':'Condição Climática',
                    'Time_taken(min)': 'Tempo para entrega'}))
    return fig

def media_entrega_cidade(df1):
    cols = ['Time_taken(min)', 'City']
    df1_aux = df1.loc[:, cols].groupby('City').mean().reset_index()
    fig = (px.bar(df1_aux, x='City', y='Time_taken(min)',
                labels={'City':'Cidade',
                'Time_taken(min)': 'Tempo para entrega'}))
    return fig

def retirarNaN(df1, x):
    linhas_selecionadas = df1[x] != "NaN "
    return df1.loc[linhas_selecionadas, :].copy()

df1 = retirarNaN(df1, "Road_traffic_density")
df1 = retirarNaN(df1, "multiple_deliveries")
df1 = retirarNaN(df1, "Delivery_person_Age")
df1 = retirarNaN(df1, "City")
df1 = retirarNaN(df1, "Festival")
df1 = retirarNaN(df1, "Time_taken(min)")
df1["Time_taken(min)"] = df1["Time_taken(min)"].str.replace("(min) ", "")

def alterarTipoColuna(df1, coluna, tipofinal):
    df1[coluna] = df1[coluna].astype(tipofinal)

alterarTipoColuna(df1, "Delivery_person_Age", int)
alterarTipoColuna(df1, "Delivery_person_Ratings", float)
# alterarTipoColuna(df1, 'Time_taken(min)', int)
alterarTipoColuna(df1, "multiple_deliveries", int)
df1 = df1.reset_index()

df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], dayfirst=True, format="%d-%m-%Y")

def tirarespaços(df1, x):
    df1 = df1.reset_index(drop=True)
    df1[x] = df1[x].str.strip()
    return df1

df1 = df1.reset_index()
df1 = tirarespaços(df1, "ID")
df1 = tirarespaços(df1, "Road_traffic_density")
df1 = tirarespaços(df1, "Type_of_order")
df1 = tirarespaços(df1, "Type_of_vehicle")
df1 = tirarespaços(df1, "City")

# =================================================================================
# STREAMLIT
# SIDEBAR
image = Image.open('Logo-data-science1.png')
st.sidebar.image(image, width=250)
st.header('Marketplace - Visão Entregadores')
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    "Qual a condição do trânsito?",
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS(Juliano Nicoletti)')

#Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# LAYOUT STREAMLIT
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '--', '--'])

with tab1:
    with st.container():
        st.header('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)          
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)
        with col3: 
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_condicao)
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição',pior_condicao)
            
    with st.container():
        st.markdown('''---''')
        st.header('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação médias por entregador')
            avaliacao_media_entregador = avali_porentregador(df1)
            st.dataframe(avaliacao_media_entregador, height=640)
            
        with col2:
            st.markdown('##### Avaliação média por transito')
            media_tipodetrafego = avali_portransito(df1)
            st.dataframe(media_tipodetrafego)
            
            st.markdown('##### Avaliação média por clima')
            media_std_condicao = avaliacao_media_entregador
            st.dataframe(media_std_condicao)
    
    with st.container():
        st.markdown('''---''')
        st.header('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### 10 entregadores mais rápidos')
            df3 = ordenar_entregador(df1, ordenacao=True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('##### 10 entregadores mais lentos')
            df3 = ordenar_entregador(df1, ordenacao=False)
            st.dataframe(df3)
    with st.container():
        st.markdown('''---''')
        col1, col2 = st.columns(2)
        with col1: 
            st.markdown('##### Média tempo entrega por condição climática')
            fig = media_entrega_clima(df1)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown('##### Tempo entrega por cidade')
            fig = media_entrega_cidade(df1)
            st.plotly_chart(fig, use_container_width=True)
            

            
        



