"""Google Sheets integration for Coverage Index."""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def connect_to_sheets(credentials_json: dict) -> gspread.Client:
    """Connect to Google Sheets using service account credentials."""
    credentials = Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
    return gspread.authorize(credentials)


def get_or_create_spreadsheet(client: gspread.Client, spreadsheet_name: str) -> gspread.Spreadsheet:
    """Get existing spreadsheet or create new one."""
    try:
        return client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        return client.create(spreadsheet_name)


def load_outlets_from_sheet(spreadsheet: gspread.Spreadsheet) -> pd.DataFrame:
    """Load outlets data from the Outlets worksheet."""
    try:
        worksheet = spreadsheet.worksheet("Outlets")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.WorksheetNotFound:
        return pd.DataFrame()


def load_outlets_from_excel(file_path: str) -> pd.DataFrame:
    """Load outlets from local Excel file."""
    return pd.read_excel(file_path)


def save_outlets_to_sheet(spreadsheet: gspread.Spreadsheet, outlets_df: pd.DataFrame):
    """Save outlets DataFrame to Google Sheets."""
    try:
        worksheet = spreadsheet.worksheet("Outlets")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Outlets", rows=500, cols=10)

    # Clear and update
    worksheet.clear()
    worksheet.update([outlets_df.columns.tolist()] + outlets_df.values.tolist())


def load_clients_from_sheet(spreadsheet: gspread.Spreadsheet) -> list:
    """Load client configurations from the Clients worksheet."""
    try:
        worksheet = spreadsheet.worksheet("Clients")
        data = worksheet.get_all_records()

        clients = []
        for row in data:
            client = {
                "name": row.get("Name", ""),
                "industry": row.get("Industry", ""),
                "spokesperson": row.get("Spokesperson", ""),
                "key_messages": parse_list_field(row.get("Key Messages", "")),
                "competitors": parse_list_field(row.get("Competitors", "")),
            }
            if client["name"]:
                clients.append(client)

        return clients
    except gspread.WorksheetNotFound:
        return []


def save_client_to_sheet(spreadsheet: gspread.Spreadsheet, client: dict):
    """Save a client configuration to Google Sheets."""
    try:
        worksheet = spreadsheet.worksheet("Clients")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Clients", rows=100, cols=10)
        worksheet.update("A1:E1", [["Name", "Industry", "Spokesperson", "Key Messages", "Competitors"]])

    # Find existing row or append
    existing = worksheet.get_all_records()
    row_num = None
    for i, row in enumerate(existing):
        if row.get("Name") == client["name"]:
            row_num = i + 2  # +2 for header and 0-index
            break

    row_data = [
        client["name"],
        client.get("industry", ""),
        client.get("spokesperson", ""),
        format_list_field(client.get("key_messages", [])),
        format_list_field(client.get("competitors", [])),
    ]

    if row_num:
        worksheet.update(f"A{row_num}:E{row_num}", [row_data])
    else:
        worksheet.append_row(row_data)


def delete_client_from_sheet(spreadsheet: gspread.Spreadsheet, client_name: str):
    """Delete a client from Google Sheets."""
    try:
        worksheet = spreadsheet.worksheet("Clients")
        cell = worksheet.find(client_name)
        if cell:
            worksheet.delete_rows(cell.row)
    except (gspread.WorksheetNotFound, gspread.CellNotFound):
        pass


def parse_list_field(value: str) -> list:
    """Parse a newline or semicolon separated string into a list."""
    if not value:
        return []
    # Try newline first, then semicolon
    if "\n" in value:
        return [item.strip() for item in value.split("\n") if item.strip()]
    return [item.strip() for item in value.split(";") if item.strip()]


def format_list_field(items: list) -> str:
    """Format a list as newline-separated string for storage."""
    return "\n".join(items)


def add_outlet_to_sheet(spreadsheet: gspread.Spreadsheet, outlet: dict):
    """Add a new outlet to the database."""
    try:
        worksheet = spreadsheet.worksheet("Outlets")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Outlets", rows=500, cols=10)
        worksheet.update("A1:E1", [["Media Outlet", "Tier", "Outlet Type", "Impressions", "Web Domain"]])

    row_data = [
        outlet.get("name", ""),
        outlet.get("tier", 3),
        outlet.get("type", "Online"),
        outlet.get("impressions", 0),
        outlet.get("domain", ""),
    ]
    worksheet.append_row(row_data)
