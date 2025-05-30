from code.googleUtils import SPREADSHEET_ID, get_credentials, download_sheet_as_csv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import csv


def find_new_rows(analyzed_path, saved_all_path, output_path, empty_columns_count):
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


def prepend_missing_rows(service, sheet_name, missing_rows_path, range, empty_columns_count):
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


def merge(emptyColCount, sheet_name, cleaned_path, saved_all_path, live_missing_path, range="A1:Z1000"):
    """Main function to export data to Google Sheets."""
    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)

        download_sheet_as_csv(service, sheet_name, saved_all_path, range)

        find_new_rows(cleaned_path, saved_all_path, live_missing_path, emptyColCount)

        # prepend_missing_rows(service, sheet_name, live_missing_path, range, emptyColCount)
        print(f"Data successfully updated.")
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    merge(
        emptyColCount=2,
        sheet_name="Main",
        cleaned_path="leie/live_data_parsed.csv",
        saved_all_path="leie/sheet_downloaded.csv",
        live_missing_path="leie/live_missing.csv"
    )
