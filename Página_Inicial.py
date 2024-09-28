import gspread
import pandas as pd
import numpy as np
import gspread_dataframe as gd
from oauth2client.service_account import ServiceAccountCredentials

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('mobilize-data.json', scope)

# authorize the clientsheet 
client = gspread.authorize(creds)

planilha = client.open('Consolidado V1 - SESI > iFood')

data = planilha.worksheet("acompanhamento geral_atual.")

indice_coluna = 8
coluna = data.col_values(indice_coluna)

print(coluna)