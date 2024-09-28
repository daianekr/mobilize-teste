import gspread
import json
import airbyte as ab
import pandas as pd
import numpy as np
import gspread_dataframe as gd
import streamlit as st
from itertools import islice
from oauth2client.service_account import ServiceAccountCredentials

PATH_to_KEY = 'mobilize-data.json'
URL_to_SPREADSHEET = "https://docs.google.com/spreadsheets/d/1sgUe83VbTZPhH5dtBtuGJpk6Pa1tqhUE4QCtOYvZ6ik/edit?gid=280735631#gid=280735631"

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(PATH_to_KEY, scope)
client = gspread.authorize(creds)
planilha = client.open('Consolidado V1 - SESI > iFood')
data = planilha.worksheet("acompanhamento geral_atual.")

# indice_coluna = 8
# coluna = data.col_values(indice_coluna)

# print(coluna)

st.title("Mobilize <> Ifood")

