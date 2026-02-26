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


def load_outlets_from_excel(file_path: str) -> pd.DataFrame:
    """Load outlets from local Excel file."""
    return pd.read_excel(file_path)


def load_outlets_from_sheet(spreadsheet: gspread.Spreadsheet) -> pd.DataFrame:
    """Load outlets data from the Outlets worksheet."""
    try:
        worksheet = spreadsheet.worksheet("Outlets")
        data = worksheet.get_all_records()
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame()
    except gspread.WorksheetNotFound:
        return pd.DataFrame()


def save_outlets_to_sheet(spreadsheet: gspread.Spreadsheet, outlets_df: pd.DataFrame):
    """Save outlets DataFrame to Google Sheets."""
    try:
        worksheet = spreadsheet.worksheet("Outlets")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Outlets", rows=500, cols=10)

    worksheet.clear()
    if not outlets_df.empty:
        # Convert all values to strings to avoid gspread serialization issues
        header = outlets_df.columns.tolist()
        rows = outlets_df.astype(str).values.tolist()
        worksheet.update([header] + rows)


def load_clients_from_sheet(spreadsheet: gspread.Spreadsheet) -> dict:
    """Load client configurations from the Clients worksheet.

    The Clients sheet stores one row per client with columns:
    Name, Industry, CampaignsJSON

    CampaignsJSON is a JSON string containing the full campaigns dict.
    Returns a dict of client_name -> client data (matching app session_state format).
    """
    try:
        worksheet = spreadsheet.worksheet("Clients")
        data = worksheet.get_all_records()

        clients = {}
        for row in data:
            name = row.get("Name", "")
            if not name:
                continue

            campaigns_raw = row.get("CampaignsJSON", "")
            campaigns = {}
            if campaigns_raw:
                try:
                    campaigns = json.loads(campaigns_raw)
                except (json.JSONDecodeError, TypeError):
                    pass

            clients[name] = {
                "name": name,
                "industry": row.get("Industry", ""),
                "campaigns": campaigns,
            }

        return clients
    except gspread.WorksheetNotFound:
        return {}


def save_client_to_sheet(spreadsheet: gspread.Spreadsheet, client_name: str, client_data: dict):
    """Save a single client to the Clients sheet (insert or update)."""
    try:
        worksheet = spreadsheet.worksheet("Clients")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Clients", rows=100, cols=5)
        worksheet.update("A1:C1", [["Name", "Industry", "CampaignsJSON"]])

    campaigns_json = json.dumps(client_data.get("campaigns", {}))
    row_data = [
        client_name,
        client_data.get("industry", ""),
        campaigns_json,
    ]

    # Find existing row or append
    existing = worksheet.get_all_records()
    row_num = None
    for i, row in enumerate(existing):
        if row.get("Name") == client_name:
            row_num = i + 2  # +2 for header and 0-index
            break

    if row_num:
        worksheet.update(f"A{row_num}:C{row_num}", [row_data])
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


def parse_list_field(value: str) -> list:
    """Parse a newline or semicolon separated string into a list."""
    if not value:
        return []
    if "\n" in value:
        return [item.strip() for item in value.split("\n") if item.strip()]
    return [item.strip() for item in value.split(";") if item.strip()]


def format_list_field(items: list) -> str:
    """Format a list as newline-separated string for storage."""
    return "\n".join(items)
