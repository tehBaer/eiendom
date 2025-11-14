from typing import List

from main.googleUtils import SPREADSHEET_ID, get_credentials, download_sheet_as_csv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import csv


import os



def align_columns(df_to_align: pd.DataFrame, reference_df: pd.DataFrame) -> pd.DataFrame:
    """Align a DataFrame to have the same column order as the other"""
    return df_to_align.reindex(columns=reference_df.columns)



def try_filter_new_ads(path_live, path_sheets_downloaded, path_output, headers: List[str]) -> bool:
    try:
        # Load the CSV files
        live_df = pd.read_csv(path_live, usecols=headers)
        sheets_df = pd.read_csv(
            path_sheets_downloaded,
            header=None,
            names=headers,
            usecols=headers,
            on_bad_lines='skip'
        )

        # Check for required columns
        for col in headers:
            if col not in sheets_df.columns:
                raise ValueError(f'Missing required column in header: {col}')

        # Find rows in live_df not in sheets_df
        missing_ads = live_df[~live_df['Finnkode'].isin(sheets_df['Finnkode'])]
        print("Found", len(missing_ads), "missing ads.")

        if missing_ads.empty:
            print("No new rows to save. The output file will not be created.")
            return

        # Save only the specified columns
        missing_ads.to_csv(path_output, index=False, columns=headers)
        print(f"Missing rows saved to '{path_output}'.")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def filter_new_property_ads(analyzed_path, saved_all_path, output_path, empty_columns_count):
    """Find rows in analyzed.csv not present in sheets.csv and save them to a new CSV."""
    try:
        # Load the CSV files
        analyzed_df = pd.read_csv(analyzed_path)
        sheets_df = pd.read_csv(
            saved_all_path,
            header=None,
            names=['Finnkode', 'Tilgjengelighet', 'Adresse', 'Postnummer', 'Leiepris',
                   'Depositum', 'URL',
                   # 'Innflytting', 'Utflytting',
                   'AREAL', 'PRIS KVM'],
            on_bad_lines='skip'
        )

        # Clean and standardize the Finnkode column
        analyzed_df['Finnkode'] = analyzed_df['Finnkode'].astype(str).str.strip()
        sheets_df['Finnkode'] = sheets_df['Finnkode'].astype(str).str.strip()

        # Align columns for comparison
        common_columns = analyzed_df.columns.intersection(sheets_df.columns)
        analyzed_df = analyzed_df[common_columns]
        sheets_df = sheets_df[common_columns]

        # Find rows in analyzed.csv not in sheets.csv
        missing_finnkode = analyzed_df[~analyzed_df['Finnkode'].isin(sheets_df['Finnkode'])]

        # Check if there are missing rows
        if missing_finnkode.empty:
            print("No new rows to save. The output file will not be created.")
            return

        # Add empty columns to the missing rows

        for i in range(empty_columns_count):
            missing_finnkode.insert(0, f'Empty{i + 1}', '')

        # Save missing rows to a new CSV file
        missing_finnkode.to_csv(output_path, index=False)
        print(f"Missing rows saved to '{output_path}'.")

    except Exception as e:
        print(f"An error occurred: {e}")


def prepend_missing_ads(service, sheet_name, missing_rows_path, range, empty_columns_count):
    """Prepend missing rows below the header of the specified sheet, ensuring numeric values are recognized as numbers."""
    try:
        # Read missing rows from the CSV file
        with open(missing_rows_path, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            missing_rows = list(csv_reader)

        # Separate header and data
        header = missing_rows[0]
        missing_rows = missing_rows[1:]

        # Ensure each row has exactly `empty_columns_count` empty cells at the start
        padded_missing_rows = [
            ([""] * empty_columns_count + row[empty_columns_count:])[:len(header)]
            for row in missing_rows
        ]

        # Retrieve existing data from the sheet
        range_name = f"{sheet_name}!{range}"  # Adjust the range as needed
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        existing_data = result.get("values", [])

        # Combine header, existing data, and padded missing rows
        updated_data = [existing_data[0]] + padded_missing_rows + existing_data[1:]

        # Write the updated data back to the sheet
        body = {"values": updated_data}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",  # Use USER_ENTERED to preserve formatting
            body=body,
        ).execute()

        print(f"Missing rows have been prepended below the header in the sheet: {sheet_name}")

    except Exception as e:
        print(f"An error occurred: {e}")


def merge_above(emptyColCount, sheet_name, path_live_parsed, path_downloaded_spreadsheet, path_live_missing,
                range="A1:Z1000"):
    """Main function to export data to Google Sheets."""
    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)

        download_sheet_as_csv(service, sheet_name, path_downloaded_spreadsheet, range)

        filter_new_property_ads(path_live_parsed, path_downloaded_spreadsheet, path_live_missing, emptyColCount)

        prepend_missing_ads(service, sheet_name, path_live_missing, range, emptyColCount)
        print(f"Data successfully updated.")
    except HttpError as err:
        print(err)

def check_missing_headers(df: pd.DataFrame, headers_to_use: List[str]) -> List[str]:
    missing_headers = [h for h in headers_to_use if h not in df.columns]
    return missing_headers

def try_merge_below(projectName, sheet_name, path_live, path_downloaded_sheet, path_live_missing, headers_to_use: List[str]):
    """Checks for missing headers in both CSVs before merging below."""
    # Check headers in live data
    live_df = pd.read_csv(path_live)
    missing_in_live = [h for h in headers_to_use if h not in live_df.columns]
    if missing_in_live:
        raise Exception(f"Missing required headers in live data: {missing_in_live}")

    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)
        download_sheet_as_csv(service, sheet_name, path_downloaded_sheet)
    except HttpError as err:
        print(err)
    # Check headers in downloaded sheet
    sheet_df = pd.read_csv(path_downloaded_sheet)
    missing_in_sheet = [h for h in headers_to_use if h not in sheet_df.columns]
    if missing_in_sheet:
        raise Exception(f"Missing required headers in sheet: {missing_in_sheet}")

    filtered_successfully = try_filter_new_ads(path_live, path_downloaded_sheet, path_live_missing, headers_to_use)
    if (filtered_successfully):
        append_missing_ads(service, sheet_name, path_live_missing)


def append_missing_ads(service, sheet_name, missing_rows_path):
    try:
        # Read missing rows from the CSV file
        with open(missing_rows_path, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            missing_rows = list(csv_reader)

        # Separate header and data
        header = missing_rows[0]
        missing_rows = missing_rows[1:]

        # Retrieve existing data from the sheet to find the next available row
        range_name = f"{sheet_name}!A1:Z1000"  # Adjust the range as needed
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        existing_data = result.get("values", [])
        next_row_index = len(existing_data) + 1  # +1 for 1-based index in Sheets

        # Write the missing rows to the sheet starting from the next available row
        body = {"values": missing_rows}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A{next_row_index}",
            valueInputOption="USER_ENTERED",  # Use USER_ENTERED to preserve formatting
            body=body,
        ).execute()

        print(f"Missing rows have been appended to the sheet: {sheet_name}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    merge_above(
        emptyColCount=3,
        sheet_name="Main",
        path_live_parsed="leie/live_data_parsed.csv",
        path_downloaded_spreadsheet="leie/sheet_downloaded.csv",
        path_live_missing="leie/live_missing.csv"
    )
