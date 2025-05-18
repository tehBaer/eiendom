﻿import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import csv

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
    """Read data from a CSV file and process it."""
    with open(file_path, "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        data = list(csv_reader)

    # Add hyperlink to Finnkode and remove URL column
    header = data[0]
    if "URL" in header and "Finnkode" in header:
        url_index = header.index("URL")
        finnkode_index = header.index("Finnkode")

        # Update header
        header.pop(url_index)

        # Update rows
        for row in data[1:]:
            row[finnkode_index] = f'=HYPERLINK("{row[url_index]}", "{row[finnkode_index]}")'
            row.pop(url_index)
    return data


def download_sheet_as_csv(service, sheet_name, output_file, range):
    """Download data from a specific sheet and save it as a CSV file."""
    range_name = f"{sheet_name}!{range}"  # Adjust the range as needed
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    data = result.get("values", [])

    if not data:
        print(f"No data found in sheet: {sheet_name}")
        return

    # Write data to a CSV file
    with open(output_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"Data from sheet '{sheet_name}' has been saved to '{output_file}'.")