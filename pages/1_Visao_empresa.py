import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine, Unit
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', layout='wide')

df = pd.read_csv(r"..\dataset\train.csv", skipinitialspace=True)

df1 = df.copy()

def pedido_pordia(df1):
    cols = ["ID", "Order_Date"]
    df_aux = df1.loc[:, cols].groupby("Order_Date").count().reset_index()
    fig=(px.bar(df_aux, x="Order_Date", y="ID", labels={'ID':'Orders', 'Order_Date':'Day'}))
    return fig

def pedido_portrafego(df1):
    cols=['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    df_aux['entregas_perc'] = 100 * df_aux['ID']/df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
    return fig

def pedido_trafego_cidade(df1):
    cols = ['ID', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux['perc_ID'] = 100 * df_aux['ID']/df_aux['ID'].sum()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID')
    return fig

def avali_porsemana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df1_aux = df1.loc[:, ['Delivery_person_Ratings', 'week_of_year']].groupby('week_of_year').mean().reset_index()

    fig = (px.line(df1_aux,
                    x='week_of_year',
                    y='Delivery_person_Ratings',
                    labels={'week_of_year': 'Week', 'Delivery_person_Ratings': 'Avaliação Média'}))
    return fig

def pedidos_porsemana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    
    fig = px.line(df_aux, x='week_of_year', y='ID', labels={'week_of_year':'Week', 'ID':'Orders'})
    return fig

def entregador_porsemana(df1):
    df1_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df1_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge(df1_aux01, df1_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    
    fig = (px.line(df_aux, x='week_of_year',
                    y='order_by_deliver',
                    labels={'week_of_year':'Week',
                            'order_by_deliver':'Pedidos por entregador'}))
    return fig

def mapa_pais(df1):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    cols_groupby=['City', 'Road_traffic_density']
    df1_aux = df1.loc[:, cols].groupby(cols_groupby).median().reset_index()
    map1 = folium.Map()
    
    for index, location_info in df1_aux.iterrows():
        folium.Marker([location_info[ 'Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info['City']).add_to(map1)
    return map1

def retirarNaN(df1, x):
    linhas_selecionadas = df1[x] != "NaN "
    return df1.loc[linhas_selecionadas, :].copy()


df1 = retirarNaN(df1, "Road_traffic_density")
df1 = retirarNaN(df1, "multiple_deliveries")
df1 = retirarNaN(df1, "Delivery_person_Age")
df1 = retirarNaN(df1, "City")
df1 = retirarNaN(df1, "Festival")
df1 = retirarNaN(df1, "Time_taken(min)")
print(df1.head(10))
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
st.header('Marketplace - Visão Cliente')
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
st.header(date_slider)
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        
        #Orders_by_Day
        st.header('Pedidos por dia')
        fig = pedido_pordia(df1)
        st.plotly_chart(fig, use_container_width=True )
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header(' Pedidos por tráfego')
            fig = pedido_portrafego(df1)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = pedido_trafego_cidade(df1)
            st.plotly_chart(fig, use_container_width=True)
    with st.container():
        st.header('Avaliações médias das entregas por semana')
        fig = avali_porsemana(df1)
        st.plotly_chart(fig, use_container_width=True)
        
        
    
with tab2:
    with st.container():
        st.header('Pedidos por semana')
        fig = pedidos_porsemana(df1)
        st.plotly_chart(fig, use_container_width=True)
    with st.container():
        st.header('Pedidos por entregador por semana')
        fig = entregador_porsemana(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header('Mapa do País')
    map1 = mapa_pais(df1)
    folium_static(map1, width=1024,height=600 )
    
    
