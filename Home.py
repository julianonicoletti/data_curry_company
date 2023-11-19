import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    layout='wide'
)

image= Image.open('Logo-data-science1.png')

st.sidebar.image(image, width=250)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes
    ### COMO UTILIZAR ESSE GROWTH DASHBOARD?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
    
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    
    -Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    
    ### Ask for Help
    - Data Sciente da Comunidade DS (Juliano Batistela Nicoletti)
    '''
)

