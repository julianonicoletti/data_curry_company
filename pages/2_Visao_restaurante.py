import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine, Unit
import streamlit as st
import datetime
from PIL import Image
import numpy as np

df = pd.read_csv(r"dataset\train.csv", skipinitialspace=True)
df1 = df.copy()

#-----------------------------
#Funções

def time_taken_festival(df1):
    cols = ['Time_taken(min)', 'Festival']
    df1_aux = df1.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['Avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    return df1_aux

def average_distance (df1):
    cols = ['Restaurant_longitude', 'Restaurant_latitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['Distance_entrega'] = (df1.loc[0:, cols]
                                    .apply(lambda x: haversine((x['Delivery_location_latitude'], x['Delivery_location_longitude']),
                                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    unit=Unit.KILOMETERS), axis=1))
    avg_distance = np.round(df1['Distance_entrega'].mean(), 2)
    return avg_distance

def mean_std_bycity (df1):
    cols = ['City', 'Time_taken(min)']
    df1_aux = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['Avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                x=df1_aux['City'],
                y=df1_aux['Avg_time'],
                error_y=dict(type='data', array=df1_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig
def mean_std_bytypeorder (df1):
    cols = ['City', 'Time_taken(min)', 'Type_of_order']
    df1_aux = (df1.loc[:, cols].groupby(['City', 'Type_of_order'])
                    .agg({'Time_taken(min)': ['mean', 'std']}))
    df1_aux.columns = ['Avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    return df1_aux

def distance_bycity(df1):
    cols = ['Restaurant_longitude', 'Restaurant_latitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['Distance_entrega'] = (df1.loc[0:, cols]
                            .apply(lambda x: haversine((x['Delivery_location_latitude'], x['Delivery_location_longitude']),
                            (x['Restaurant_latitude'], x['Restaurant_longitude']), unit=Unit.KILOMETERS), axis=1))
    avg_distance = df1.loc[:, ['City', 'Distance_entrega']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance ['City'],
                                values=avg_distance['Distance_entrega'], pull=[0.05,0,0])])
    return fig

def time_bytraffic(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df1_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['Avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    fig=px.sunburst(df1_aux, path=['City', 'Road_traffic_density'],
                    values='Avg_time', color='std_time', color_continuous_scale='icefire',
                    color_continuous_midpoint=np.average(df1_aux['std_time']))
    return fig
    

def retirarNaN(df1, x):
    """
Retorna um novo DataFrame removendo as linhas em que a coluna especificada contém o valor "NaN".
Args:
    df1 (DataFrame): O DataFrame original.
    x: O nome da coluna a ser verificada.
Returns:
    DataFrame: Um novo DataFrame contendo apenas as linhas em que a coluna especificada não contém o valor "NaN".
"""

    linhas_selecionadas = df1[x] != "NaN "
    return df1.loc[linhas_selecionadas, :].copy()

def alterarTipoColuna(df1, coluna, tipofinal):
    """
Altera o tipo de dados de uma coluna em um DataFrame.
Args:
    df1 (DataFrame): O DataFrame no qual a coluna será modificada.
    coluna: O nome da coluna a ser alterada.
    tipofinal: O tipo de dados final para a coluna.
Returns:
    None
"""

    df1[coluna] = df1[coluna].astype(tipofinal)
    
def tirarespaços(df1, x):
    """
Remove espaços em branco no início e no final de uma coluna em um DataFrame.
Args:
    df1 (DataFrame): O DataFrame no qual a coluna será modificada.
    x: O nome da coluna a ser processada.
Returns:
    DataFrame: O DataFrame modificado, com os espaços em branco removidos da coluna especificada.
"""

    df1 = df1.reset_index(drop=True)
    df1[x] = df1[x].str.strip()
    return df1

df1 = retirarNaN(df1, "Road_traffic_density")
df1 = retirarNaN(df1, "multiple_deliveries")
df1 = retirarNaN(df1, "Delivery_person_Age")
df1 = retirarNaN(df1, "City")
df1 = retirarNaN(df1, "Festival")
df1 = retirarNaN(df1, "Time_taken(min)")
df1["Time_taken(min)"] = df1["Time_taken(min)"].str.replace("(min) ", "")

alterarTipoColuna(df1, "Delivery_person_Age", int)
alterarTipoColuna(df1, "Delivery_person_Ratings", float)
alterarTipoColuna(df1, 'Time_taken(min)', int)
alterarTipoColuna(df1, "multiple_deliveries", int)
df1 = df1.reset_index()

df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], dayfirst=True, format="%d-%m-%Y")

df1 = df1.reset_index()
df1 = tirarespaços(df1, "ID")
df1 = tirarespaços(df1, "Road_traffic_density")
df1 = tirarespaços(df1, "Type_of_order")
df1 = tirarespaços(df1, "Type_of_vehicle")
df1 = tirarespaços(df1, "City")

# =================================================================================
# STREAMLIT
# SIDEBAR
st.set_page_config(page_title='Visão Restaurante', page_icon=None,
                layout="wide", initial_sidebar_state="auto",
                menu_items=None)

image = Image.open('Logo-data-science1.png')
st.sidebar.image(image, width=250)
st.header('Marketplace - Restaurantes')
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
        st.markdown('### Entregas')
        col1, col2, col3 = st.columns(3)
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)  
    
        with col2:
            avg_distance = average_distance(df1)
            col2.metric('Distância Média entregas', avg_distance)
            
        with col3:
            df1_aux = time_taken_festival(df1)
            col3.metric('Tempo médio entrega em Festival', np.round(df1_aux.loc[1, 'Avg_time'], 2))
    with st.container():
        col4, col5, col6 = st.columns(3)    
        with col4:
            col4.metric('Desvio Padrão entregas em Festival', np.round(df1_aux.loc[1, 'std_time'], 2))
        with col5:
            col5.metric('Tempo médio entregas SEM Festival', np.round(df1_aux.loc[0, 'Avg_time'], 2))
        with col6:
            col6.metric('Desvio Padrão entregas SEM Festival', np.round(df1_aux.loc[0, 'std_time'], 2))
    with st.container():
        st.markdown('''---''')
        col1, espacamento,  col2 = st.columns([1, 0.2, 1])
        with col1:
            fig = mean_std_bycity(df1)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            df1_aux = mean_std_bytypeorder(df1)
            st.dataframe(df1_aux)
            
    with st.container():
        st.markdown('''---''')
        st.markdown('#### Distribuição da distancia')
        col1, espacamento,  col2 = st.columns([1, 0.2, 1])
        with col1:
            fig = distance_bycity(df1)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = time_bytraffic(df1)
            st.plotly_chart(fig, use_container_width=True)
            
    with st.container():
        st.markdown('''---''')
        

            
        
    