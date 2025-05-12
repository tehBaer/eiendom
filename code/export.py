import csv
import os.path

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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


def download_sheet_as_csv(service, sheet_name, output_file):
    """Download data from a specific sheet and save it as a CSV file."""
    range_name = f"{sheet_name}!A1:Z1000"  # Adjust the range as needed
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



import pandas as pd

def find_new_rows(analyzed_path, sheets_path, output_path):
    """Find Finnkode IDs in analyzed.csv that are not in sheets.csv and save only those rows to a new CSV."""
    try:
        # Load the analyzed.csv and sheets.csv files
        analyzed_df = pd.read_csv(analyzed_path)
        sheets_df = pd.read_csv(sheets_path, header=None,
                                names=['Index', 'Finnkode', 'Utleid', 'Adresse', 'Postnummer', 'Leiepris',
                                       'Depositum', 'URL', 'AREAL', 'PRIS KVM'])

        # Clean and standardize the Finnkode columns
        analyzed_df['Finnkode'] = analyzed_df['Finnkode'].astype(str).str.strip()
        sheets_df['Finnkode'] = sheets_df['Finnkode'].astype(str).str.strip()

        # Debug: Print row counts
        print(f"Rows in analyzed: {len(analyzed_df)}")
        print(f"Rows in sheets: {len(sheets_df)}")

        # Find Finnkode IDs in analyzed.csv that are not in sheets.csv
        missing_finnkode = analyzed_df[~analyzed_df['Finnkode'].isin(sheets_df['Finnkode'])]

        # Debug: Print missing rows
        print(f"Missing rows: {missing_finnkode}")

        # Save only the missing Finnkode rows to a new CSV file
        missing_finnkode.to_csv(output_path, index=False)

    except Exception as e:
        print(f"An error occurred: {e}")


def prepend_missing_rows(service, sheet_name, missing_rows_path):
    """Prepend missing rows to the top of the specified sheet."""
    # Read missing rows from the CSV file
    with open(missing_rows_path, "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        missing_rows = list(csv_reader)

    # Separate header and data
    header = missing_rows[0]
    missing_rows = missing_rows[1:]

    # Retrieve existing data from the sheet
    range_name = f"{sheet_name}!A1:Z1000"  # Adjust the range as needed
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    existing_data = result.get("values", [])

    # Combine header, missing rows, and existing data
    updated_data = [header] + missing_rows + existing_data[1:]  # Keep the original header

    # Write the updated data back to the sheet
    body = {"values": updated_data}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption="RAW",
        body=body,
    ).execute()

    print(f"Missing rows have been prepended to the sheet: {sheet_name}")
def merge():
    """Main function to export data to Google Sheets."""
    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)

        download_sheet_as_csv(service, "test", "leie/_sheets.csv")

        find_new_rows("leie/analyzed.csv", "leie/_sheets.csv", "leie/_sheets_missing.csv")

        prepend_missing_rows(service, "test", "leie/_sheets_missing.csv")
        print(f"Data successfully updated.")
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    merge()
