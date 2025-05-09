import os.path
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import locale
import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1HW6-mtyK5FDGA_aL1EUyX4ZQMZozL3XXeNcqzjlRYDA"

def get_credentials():
    """Retrieve or refresh Google API credentials."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def read_csv(file_path):
    """Read data from a CSV file."""
    with open(file_path, "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        return list(csv_reader)

def get_unique_sheet_name(service, base_name):
    """Generate a unique sheet name by appending a number if needed."""
    existing_sheets = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()["sheets"]
    existing_titles = [sheet["properties"]["title"] for sheet in existing_sheets]

    sheet_name = base_name
    counter = 1
    while sheet_name in existing_titles:
        sheet_name = f"{base_name} ({counter})"
        counter += 1
    return sheet_name

def add_sheet(service, sheet_name):
    """Add a new sheet to the spreadsheet."""
    sheet_body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": sheet_name,
                        "gridProperties": {"frozenRowCount": 1},
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=sheet_body).execute()

def write_data_to_sheet(service, sheet_name, data):
    """Write data to the specified sheet."""
    range_name = f"{sheet_name}!A1"
    body = {"values": data}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption="RAW",
        body=body,
    ).execute()

def export():
    """Main function to export data to Google Sheets."""
    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)

        # Read data from the CSV file
        data = read_csv("leie/analyzed.csv")

        # Set the locale to Norwegian
        locale.setlocale(locale.LC_TIME, "nb_NO.UTF-8")

        # Generate a unique sheet name
        base_sheet_name = datetime.datetime.now().strftime("%#d. %B").capitalize()
        sheet_name = get_unique_sheet_name(service, base_sheet_name)

        # Add the sheet and write data
        add_sheet(service, sheet_name)
        write_data_to_sheet(service, sheet_name, data)

        print(f"Data successfully written to the new sheet: {sheet_name}.")
    except HttpError as err:
        print(err)

if __name__ == "__main__":
    export()