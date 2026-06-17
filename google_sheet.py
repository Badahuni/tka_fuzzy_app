import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    # Streamlit Cloud
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=SCOPES
    )

except Exception:
    # 로컬 테스트용
    creds = Credentials.from_service_account_file(
        "tka-sheet-bot.json",
        scopes=SCOPES
    )

client = gspread.authorize(creds)

sheet = client.open("TKA_Rehab_Data").sheet1


def save_to_sheet(row):
    sheet.append_row(list(row.values()))