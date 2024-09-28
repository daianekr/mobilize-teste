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


def batched(iterable, n_cols):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n_cols < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n_cols)):
        yield batch
        
@st.cache_data
def _read_service_account_secret(): 
    with open(PATH_to_KEY) as f:
        return json.load(f)
    

@st.cache_resource
def connect_to_gsheets():
    s_acc = _read_service_account_secret()
    gsheets_connection = ab.get_source(
        "source-google-sheets",
        config={
            "spreadsheet_id": URL_to_SPREADSHEET,
            "credentials": {
                "auth_type": "Service",
                "service_account_info": json.dumps(s_acc),
            },
        },
    )
    # gsheets_connection.check()  # can use to check network

    gsheets_connection.select_all_streams()
    # gsheets_connection.select_streams("ticker")  # select stream to sync
    
    return gsheets_connection

@st.cache_data
def download_data(_gsheets_connection):
    airbyte_streams = _gsheets_connection.read()

    ticker_df = airbyte_streams["ticker"].to_pandas()

    history_dfs = {}
    for ticker in list(ticker_df["ticker"]):
        d = airbyte_streams[ticker].to_pandas()
        history_dfs[ticker] = d

    return ticker_df, history_dfs