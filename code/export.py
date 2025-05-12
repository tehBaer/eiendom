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



def find_new_rows(analyzed_path, sheets_path, output_path, empty_columns_count):
    """Find Finnkode IDs in analyzed.csv that are not in sheets.csv and save only those rows to a new CSV."""
    try:
        # Load the analyzed.csv and sheets.csv files with error handling for inconsistent rows
        analyzed_df = pd.read_csv(analyzed_path)
        sheets_df = pd.read_csv(sheets_path, header=None,
                                names=['Index', 'Finnkode', 'Utleid', 'Adresse', 'Postnummer', 'Leiepris',
                                       'Depositum', 'URL', 'AREAL', 'PRIS KVM'],
                                on_bad_lines='skip')  # Skip problematic rows

        # Clean and standardize the Finnkode columns
        analyzed_df['Finnkode'] = analyzed_df['Finnkode'].astype(str).str.strip()
        sheets_df['Finnkode'] = sheets_df['Finnkode'].astype(str).str.strip()

        # Align columns for comparison
        common_columns = analyzed_df.columns.intersection(sheets_df.columns)
        analyzed_df = analyzed_df[common_columns]
        sheets_df = sheets_df[common_columns]

        # Find Finnkode IDs in analyzed.csv that are not in sheets.csv
        missing_finnkode = analyzed_df[~analyzed_df['Finnkode'].isin(sheets_df['Finnkode'])]

        # Add empty columns to the missing rows
        for i in range(empty_columns_count):
            missing_finnkode.insert(0, '', '')

        # Save only the missing Finnkode rows to a new CSV file
        missing_finnkode.to_csv(output_path, index=False)

    except Exception as e:
        print(f"An error occurred: {e}")


def prepend_missing_rows(service, sheet_name, missing_rows_path, range, empty_columns_count):
    """Prepend missing rows below the header of the specified sheet, filling columns before and after the range with empty cells."""
    # Read missing rows from the CSV file
    with open(missing_rows_path, "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        missing_rows = list(csv_reader)

    # Separate header and data
    header = missing_rows[0]
    missing_rows = missing_rows[1:]

    # Retrieve existing data from the sheet
    range_name = f"{sheet_name}!{range}"  # Adjust the range as needed
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    existing_data = result.get("values", [])

    # Determine the number of columns in the full sheet
    full_range = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    total_columns = full_range["sheets"][0]["properties"]["gridProperties"]["columnCount"]
    # Determine the start and end columns of the specified range
    start_column = ord(range.split(":")[0][0]) - ord("A")
    end_column = ord(range.split(":")[1][0]) - ord("A") + 1

    # Pad missing rows with empty cells before and after the range
    padded_missing_rows = [
        [""] * empty_columns_count + [""] * start_column + row + [""] * (total_columns - end_column)
        for row in missing_rows
    ]

    # Combine header, existing data, and padded missing rows
    updated_data = [existing_data[0]] + padded_missing_rows + existing_data[1:]

    # Write the updated data back to the sheet
    body = {"values": updated_data}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        body=body,
    ).execute()

    print(f"Missing rows have been prepended below the header in the sheet: {sheet_name}")



def merge():
    """Main function to export data to Google Sheets."""
    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)

        range = "A1:Z1000"
        emptyColCount = 2

        download_sheet_as_csv(service, "test", "leie/_sheets.csv", range)

        find_new_rows("leie/analyzed.csv", "leie/_sheets.csv", "leie/_sheets_missing.csv", emptyColCount)

        # prepend_missing_rows(service, "test", "leie/_sheets_missing.csv", range, emptyColCount)
        print(f"Data successfully updated.")
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    merge()
