import pandas as pd
import numpy as np
import streamlit as st
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype
from streamlit_gsheets import GSheetsConnection
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px 

st.set_page_config(
    page_title="Mobilize<>Ifood",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Relatório de Presenças no Programa *Meu Diploma*"
    }
)

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(
    worksheet="acompanhamento_geral_atual.",
    ttl="10m"
)

# PATH_to_KEY = "mobilize-data.json"



# scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name("mobilize-data.json", scope)
# client = gspread.authorize(creds)
# sheet = client.open('Consolidado V1 - SESI > iFood').worksheet('acompanhamento geral_atual.')
# data = sheet.get_all_values()
# headers = data[0]
# data = data[1:]

colunas = ['Nome','Status','OBS','parceria_ifood','RM','unidade_sesi','CPF', 'email_sesi','phone','email_ifood','Semana 0\n05 a 09/08','1ª semana\n12 a 16/08','2ª semana\n19 a 23/08','3ª semana\n26 a 30/08','4ª semana\n02 a 06/09','5ª semana\n09 a 13/09','6ª semana\n16 a 20/09','já foi a alguma aula?','Foi 1x', 'Foi 2x', 'Foi 3x', 'Foi 4x',
       'Foi 5x','Foi 6x','Já frenquentou alguma aula presencial? Se sim, qual?']

df['RM'] = df['RM'].astype(str)
df['CPF'] = df['CPF'].astype(str)
df['phone'] = df['phone'].astype(str)
df['email_sesi'] = df['email_sesi'].astype(str)
df['email_ifood'] = df['email_ifood'].astype(str)

df_1 = df[colunas]

df_1 = df_1.rename(columns={'Nome':'Nome', 'Status':'Status', 'OBS':'Observação', 'parceria_ifood':'Parceria Ifood',
       'RM':'Nº Matrícula', 'unidade_sesi':'Unidade SESI',
       'email_sesi': 'E-mail SESI', 'phone':'Telefone', 'email_ifood':'E-mail Ifood', 'Semana 0\n05 a 09/08':'Semana 0',
       '1ª semana\n12 a 16/08':'Semana 1', '2ª semana\n19 a 23/08': 'Semana 2',
       '3ª semana\n26 a 30/08': 'Semana 3', '4ª semana\n02 a 06/09': 'Semana 4',
       '5ª semana\n09 a 13/09': 'Semana 5', '6ª semana\n16 a 20/09': 'Semana 6',
       'já foi a alguma aula?': 'Já foi a alguma aula?', 'Foi 1x': 'Foi 1 Vez', 'Foi 2x': 'Foi 2 Vezes', 'Foi 3x': 'Foi 3 Vezes', 'Foi 4x': 'Foi 4 Vezes',
       'Foi 5x': 'Foi 5 Vezes','Foi 6x': 'Foi 6 Vezes'})

st.title("Programa Meu Diploma de Ensino Médio")

st.text("")
st.text("")

def display_overview(df_1):
    st.dataframe(
        df_1, 
        hide_index=True
    )

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.sidebar.checkbox("Adicionar Filtros", key="filter_checkbox")

    if not modify:
        return df

    df = df.copy()

    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

        if is_numeric_dtype(df[col]) and (df[col] == df[col].astype(int)).all():
            df[col] = df[col].astype(int)

    modification_container = st.sidebar.container()

    with modification_container:
        to_filter_columns = st.multiselect(
            "Filtrar pela Coluna: ", 
            df.columns,
            key="multiselect_columns"
        )
        for i, column in enumerate(to_filter_columns):
            left, right = st.columns((1, 20))

            if isinstance(df[column].dtype, pd.CategoricalDtype) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                    key=f"multiselect_{column}_{i}"
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                    key=f"slider_{column}_{i}"
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                    key=f"date_input_{column}_{i}"
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Digite uma substring pelo que quer filtrar de {column}",
                    key=f"text_input_{column}_{i}"
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


filtered = filter_dataframe(df_1)

# matriculados = filtered[filtered['Status'] == 'Matriculado']

total = filtered.shape[0]

total_mat = (filtered['Status'] == 'Matriculado')
total_mat = total_mat.sum()

total_ent = (filtered['Parceria Ifood'] == 'Sou entregador (a) iFood')
total_ent = total_ent.sum()

total_don = (filtered['Parceria Ifood'] == 'Sou dono (a) de uma loja')
total_don = total_don.sum()

total_fun = (filtered['Parceria Ifood'] == 'Sou Funcionário (a) de uma loja')
total_fun = total_fun.sum()

total_p_0 = (filtered['Semana 0'] == 'PRESENTE')
total_p_0 = total_p_0.sum()

total_p_1 = (filtered['Semana 1'] == 'PRESENTE')
total_p_1 = total_p_1.sum()

total_p_2 = (filtered['Semana 2'] == 'PRESENTE')
total_p_2 = total_p_2.sum()

total_p_3 = (filtered['Semana 3'] == 'PRESENTE')
total_p_3 = total_p_3.sum()

total_p_4 = (filtered['Semana 4'] == 'PRESENTE')
total_p_4 = total_p_4.sum()

total_p_5 = (filtered['Semana 5'] == 'PRESENTE')
total_p_5 = total_p_5.sum()

total_f = (filtered['Já foi a alguma aula?'] == 'Sim')
total_f = total_f.sum()

total_1 = (filtered['Foi 1 Vez'] == 'Sim')
total_1 = total_1.sum()

total_2 = (filtered['Foi 2 Vezes'] == 'Sim')
total_2 = total_2.sum()

total_3 = (filtered['Foi 3 Vezes'] == 'Sim')
total_3 = total_3.sum()

total_4 = (filtered['Foi 4 Vezes'] == 'Sim')
total_4 = total_4.sum()

total_5 = (filtered['Foi 5 Vezes'] == 'Sim')
total_5 = total_5.sum()

total_6 = (filtered['Foi 6 Vezes'] == 'Sim')
total_6 = total_6.sum()

st.markdown("### Visão Geral")

st.text("")
st.text("")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Total </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total}</span>
        </div>
        """, unsafe_allow_html=True)

    
with col2:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Matriculados </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_mat}</span>
        </div>
        """, unsafe_allow_html=True)  
    
with col3:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Entregadores </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_ent}</span>
        </div>
        """, unsafe_allow_html=True)
      
with col4:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Donos de Loja </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_don}</span>
        </div>
        """, unsafe_allow_html=True)
     
with col5:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Func. de Loja </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_fun}</span>
        </div>
        """, unsafe_allow_html=True)
       
with col6:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;">  </span><br>
            <span style="font-size: 36px; font-weight: bold;"> </span>
        </div>
        """, unsafe_allow_html=True)
    
st.divider()

st.markdown("### Presença Semanal")

st.text("")
st.text("")

col7, col8, col9, col10, col11, col12 = st.columns(6)

with col7:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Semana 0 </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_p_0}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col8:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Semana 1 </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_p_1}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col9:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Semana 2 </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_p_2}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col10:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Semana 3 </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_p_3}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col11:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Semana 4 </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_p_4}</span>
        </div>
        """, unsafe_allow_html=True)
    

with col12:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Semana 5 </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_p_5}</span>
        </div>
        """, unsafe_allow_html=True)
    
st.divider()

st.markdown("### Frequência ")

st.text("")
st.text("")

col13, col14, col15, col16, col17, col18, col19 = st.columns(7)

with col13:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Foi a Aula </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_f}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col14:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Foi 1 vez </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_1}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col15:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Foi 2 vezes </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_2}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col16:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Foi 3 vezes </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_3}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col17:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Foi 4 vezes </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_4}</span>
        </div>
        """, unsafe_allow_html=True)
    

with col18:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Foi 5 vezes </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_5}</span>
        </div>
        """, unsafe_allow_html=True)
    
with col19:
    st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 14px;"> Foi 6 vezes </span><br>
            <span style="font-size: 36px; font-weight: bold;">{total_6}</span>
        </div>
        """, unsafe_allow_html=True)
    
st.divider()

st.text("")
st.text("")

parceria_counts = filtered['Parceria Ifood'].value_counts().reset_index()
parceria_counts.columns = ['Parceria', 'Contagem']

with st.expander("Clique para ver os dados brutos"):
    display_overview(filtered)


fig1 = px.bar(parceria_counts, 
              x='Parceria', 
              y='Contagem', 
              title='Total de Matriculados por Status Parceria com iFood', 
              labels={'Parceria': '', 'Contagem': ''},
              color='Parceria')

fig1.update_traces(
    texttemplate='%{y}',  
    textposition='inside'  
)

fig1.update_layout(
    xaxis_tickangle=0,  
    height=600,  
    xaxis=dict(
        tickmode='auto',  
        nticks=20 
    ),
    yaxis=dict(
         
        gridcolor="LightGrey"  
    ),
    bargap=0.3
)
st.plotly_chart(fig1)






