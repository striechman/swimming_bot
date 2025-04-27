import gspread
import json
import os
from google.oauth2.service_account import Credentials

def get_sheet():
    credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
    creds = Credentials.from_service_account_info(credentials_info)
    gc = gspread.authorize(creds)
    sheet_id = os.getenv('SHEET_ID')
    return gc.open_by_key(sheet_id).sheet1

def find_today_row(sheet):
    from datetime import datetime
    today = datetime.now().strftime("%d/%m/%Y")
    cells = sheet.findall(today)
    if not cells:
        sheet.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
        cells = sheet.findall(today)
    return cells[0].row

def update_cell(sheet, row, col, value):
    sheet.update_cell(row, col, value)

def append_row(sheet, values):
    sheet.append_row(values)
