import io
import os
import sys

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# # Setting Up Google OAuth for Document Export

# ## For App Administrator (One-time setup)

# 1. Go to [Google Cloud Console](https://console.cloud.google.com)
# 2. Create a new project or select existing
# 3. Enable Google Drive API
# 4. Create OAuth 2.0 credentials:
#    - Application type: Desktop app
#    - Download the client secret JSON

# ## For End Users

# ### Option A: Shared Credentials (Recommended for Teams)
# 1. Get the `credentials.json` file from your administrator via:
#    - Secure file sharing (e.g., 1Password, internal drive)
#    - Encrypted email
#    - USB drive in person
# 2. Place in `tmp/credentials.json`
# 3. Run the script - you'll authenticate with YOUR Google account

# ### Option B: Create Your Own OAuth App
# 1. Follow administrator steps above for your own Google account
# 2. Download your own client secret
# 3. Use your personal OAuth app

# ## Security Notes
# - Each user authenticates individually (personal tokens)
# - Client secret is shared, but tokens are personal
# - Never commit credentials to Git
# - Consider rotating credentials periodically

# OAuth 2.0 Scopes for Google APIs
# Documentation: https://developers.google.com/identity/protocols/oauth2/scopes

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
]

# Test documents for development
TEST_DOCUMENTS = {
    "doc": {
        "url": "https://docs.google.com/document/d/13OkypJ3u_7Jq6kEhKhjEFwHQ12oPFDKXVzFjYW4XLdk/edit",
        "id": "13OkypJ3u_7Jq6kEhKhjEFwHQ12oPFDKXVzFjYW4XLdk",
        "type": "document",
    },
    "sheet": {
        "url": "https://docs.google.com/spreadsheets/d/1knVzlMW0l0X4c7gkoiuaGql1zuFgEGwHHBsj-ygUTnc/edit",
        "id": "1knVzlMW0l0X4c7gkoiuaGql1zuFgEGwHHBsj-ygUTnc",
        "type": "spreadsheet",
    },
    "slides": {
        "url": "https://docs.google.com/presentation/d/1Kcrix7wfgv5Bk4yIxBLduYFmWlBpxfDZhh6QOeT8mHg/edit",
        "id": "1Kcrix7wfgv5Bk4yIxBLduYFmWlBpxfDZhh6QOeT8mHg",
        "type": "presentation",
    },
}

# Available export formats by document type
EXPORT_FORMATS = {
    "document": {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "odt": "application/vnd.oasis.opendocument.text",
        "rtf": "application/rtf",
        "txt": "text/plain",
        "html": "text/html",
        "epub": "application/epub+zip",
        "zip": "application/zip",  # HTML zipped
    },
    "spreadsheet": {
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ods": "application/x-vnd.oasis.opendocument.spreadsheet",
        "csv": "text/csv",
        "tsv": "text/tab-separated-values",
        "zip": "application/zip",  # HTML zipped
    },
    "presentation": {
        "pdf": "application/pdf",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "odp": "application/vnd.oasis.opendocument.presentation",
        "txt": "text/plain",
    },
}


def authenticate():
    creds = None
    token_path = "tmp/token_drive.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            # Update this path to your client secret file
            client_secret_path = "tmp/credentials.json"
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def get_document_title(service, file_id):
    """Get the title of the document using multiple fallback methods"""

    # Method 1: Try with supportsAllDrives=True first (most likely to work)
    try:
        print("Trying Method 1: files().get() with supportsAllDrives=True...")
        file = service.files().get(fileId=file_id, fields="name", supportsAllDrives=True).execute()
        title = file.get("name", "untitled")
        print(f"✅ Method 1 Success: {title}")
        return title
    except Exception as e:
        print(f"❌ Method 1 Failed: {e}")

    # Method 2: Standard files().get() API
    try:
        print("Trying Method 2: files().get() API...")
        file = service.files().get(fileId=file_id, fields="name").execute()
        title = file.get("name", "untitled")
        print(f"✅ Method 2 Success: {title}")
        return title
    except Exception as e:
        print(f"❌ Method 2 Failed: {e}")

    # Method 3: Try using export request headers
    try:
        print("Trying Method 3: Extract from export request headers...")
        request = service.files().export_media(fileId=file_id, mimeType="text/plain")
        # Execute the request but don't download - just get headers
        request.execute()
        # This might not work, but worth trying
        print("❌ Method 3: Cannot easily extract filename from export response")
    except Exception as e:
        print(f"❌ Method 3 Failed: {e}")

    # Method 4: Try Google Docs API directly (if available)
    try:
        print("Trying Method 4: Build separate docs service...")
        from googleapiclient.discovery import build

        # Get current credentials
        creds = service._http.credentials if hasattr(service, "_http") else None
        if creds:
            docs_service = build("docs", "v1", credentials=creds)
            doc = docs_service.documents().get(documentId=file_id).execute()
            title = doc.get("title", "untitled")
            print(f"✅ Method 4 Success: {title}")
            return title
    except Exception as e:
        print(f"❌ Method 4 Failed: {e}")

    print("🔄 All methods failed, using 'untitled'")
    return "untitled"


def export_document(service, file_id, export_format, mime_type, output_path):
    """Export document in specified format"""
    try:
        request = service.files().export_media(fileId=file_id, mimeType=mime_type)

        # For binary formats, we need to handle the download properly
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"  Download {int(status.progress() * 100)}%")

        # Write to file
        with open(output_path, "wb") as f:
            f.write(fh.getvalue())

        print(f"✅ Exported to {output_path}")
        return True

    except Exception as e:
        print(f"❌ Failed to export {export_format}: {e}")
        return False


def export_all_sheets_as_csv(service, spreadsheet_id, output_dir, spreadsheet_title):
    """Export all sheets from a Google Spreadsheet as separate CSV files"""
    try:
        # Build sheets service
        sheets_service = build("sheets", "v4", credentials=service._http.credentials)

        # Get spreadsheet metadata
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        title = spreadsheet["properties"]["title"]
        sheets = spreadsheet["sheets"]

        print(f"\nExporting all sheets from '{title}' as CSV files:")
        print(f"Found {len(sheets)} sheet(s)")

        # Create directory with spreadsheet name prefix
        safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in spreadsheet_title)
        csv_dir = os.path.join(output_dir, "..", f"{safe_title}_csv_sheets")
        os.makedirs(csv_dir, exist_ok=True)

        exported_sheets = []

        for sheet in sheets:
            sheet_name = sheet["properties"]["title"]
            print(f"\nExporting sheet: {sheet_name}")

            # Get sheet data
            try:
                result = (
                    sheets_service.spreadsheets()
                    .values()
                    .get(spreadsheetId=spreadsheet_id, range=f"'{sheet_name}'")
                    .execute()
                )

                values = result.get("values", [])

                if not values:
                    print(f"  ⚠️  Sheet '{sheet_name}' is empty")
                    continue

                # Sanitize filename
                safe_sheet_name = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in sheet_name)
                csv_filename = os.path.join(csv_dir, f"{safe_sheet_name}.csv")

                # Write CSV
                import csv

                with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                    csv_writer = csv.writer(csvfile)
                    for row in values:
                        csv_writer.writerow(row)

                print(f"  ✅ Exported to {csv_filename}")
                exported_sheets.append(sheet_name)

            except Exception as e:
                print(f"  ❌ Failed to export sheet '{sheet_name}': {e}")

        if exported_sheets:
            print(f"\nSuccessfully exported {len(exported_sheets)} sheet(s) to: {csv_dir}/")
            return True
        else:
            print("\n⚠️  No sheets were exported")
            return False

    except Exception as e:
        print(f"❌ Failed to export sheets as CSV: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_gdoc_all_formats.py <DOCUMENT_ID_OR_URL_OR_TEST>")
        print("\nOptions:")
        print("  - Provide a Google Doc/Sheet/Slides ID or full URL")
        print("  - Use 'test' to export all hardcoded test documents")
        print("  - Use 'doc', 'sheet', or 'slides' to export specific test document")
        print("\nTest documents:")
        for key, doc in TEST_DOCUMENTS.items():
            print(f"  {key}: {doc['url']}")
        print("\nWhat is a Google Doc ID?")
        print("The Document ID is the long string in the Google Docs URL.")
        print("For example, in this URL:")
        print("https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit")
        print("The Document ID is: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
        sys.exit(1)

    arg = sys.argv[1].strip()

    # Extract document ID from URL if a full URL is provided
    if arg.startswith("https://docs.google.com/"):
        import re

        # Match various Google Docs URL patterns
        patterns = [
            r"/document/d/([a-zA-Z0-9-_]+)",
            r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
            r"/presentation/d/([a-zA-Z0-9-_]+)",
            r"/file/d/([a-zA-Z0-9-_]+)",
        ]

        doc_id = None
        for pattern in patterns:
            match = re.search(pattern, arg)
            if match:
                doc_id = match.group(1)
                print(f"Extracted document ID from URL: {doc_id}")
                arg = doc_id
                break

        if not doc_id:
            print(f"Error: Could not extract document ID from URL: {arg}")
            print("Please provide just the document ID or a valid Google Docs/Sheets/Slides URL")
            sys.exit(1)

    # Authenticate and build service
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    documents_to_process = []

    # Check for test commands (case insensitive)
    arg_lower = arg.lower()
    if arg_lower == "test":
        # Export all test documents
        documents_to_process = [(doc["id"], doc["type"]) for doc in TEST_DOCUMENTS.values()]
    elif arg_lower in TEST_DOCUMENTS:
        # Export specific test document
        doc = TEST_DOCUMENTS[arg_lower]
        documents_to_process = [(doc["id"], doc["type"])]
    else:
        # Assume it's a document ID - try to detect type from file metadata
        doc_type = None

        # Try with supportsAllDrives=True first
        try:
            file_metadata = service.files().get(fileId=arg, fields="mimeType", supportsAllDrives=True).execute()
            mime_type = file_metadata.get("mimeType", "")

            if "document" in mime_type:
                doc_type = "document"
            elif "spreadsheet" in mime_type:
                doc_type = "spreadsheet"
            elif "presentation" in mime_type:
                doc_type = "presentation"
            else:
                print(f"Unknown document type for MIME: {mime_type}")
                doc_type = "document"  # Default fallback

        except Exception:
            # Try without supportsAllDrives
            try:
                file_metadata = service.files().get(fileId=arg, fields="mimeType").execute()
                mime_type = file_metadata.get("mimeType", "")

                if "document" in mime_type:
                    doc_type = "document"
                elif "spreadsheet" in mime_type:
                    doc_type = "spreadsheet"
                elif "presentation" in mime_type:
                    doc_type = "presentation"
                else:
                    print(f"Unknown document type for MIME: {mime_type}")
                    doc_type = "document"  # Default fallback

            except Exception as e2:
                print(f"Error detecting document type: {e2}")
                # Try to infer from the original URL if it was provided
                if sys.argv[1].strip().startswith("https://docs.google.com/"):
                    if "/spreadsheets/" in sys.argv[1]:
                        print("Detected spreadsheet from URL pattern")
                        doc_type = "spreadsheet"
                    elif "/presentation/" in sys.argv[1]:
                        print("Detected presentation from URL pattern")
                        doc_type = "presentation"
                    else:
                        print("Defaulting to document type")
                        doc_type = "document"
                else:
                    print("Defaulting to document type")
                    doc_type = "document"

        documents_to_process = [(arg, doc_type)]

    # Process each document
    for document_id, doc_type in documents_to_process:
        print(f"\nProcessing {doc_type} with ID: {document_id}")

        # Get document title for naming files
        doc_title = get_document_title(service, document_id)
        safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in doc_title)

        # Create output directory
        base_output_dir = "tmp/exports"
        os.makedirs(base_output_dir, exist_ok=True)
        output_dir = os.path.join(base_output_dir, f"{safe_title}_{doc_type}")
        os.makedirs(output_dir, exist_ok=True)
        print(f"Exporting '{doc_title}' to directory: {output_dir}/")

        # Get formats for this document type
        formats = EXPORT_FORMATS.get(doc_type, EXPORT_FORMATS["document"])

        # Export to all formats
        print(f"\nExporting to all {doc_type} formats:")
        successful_exports = []

        for format_ext, mime_type in formats.items():
            output_path = os.path.join(output_dir, f"{safe_title}.{format_ext}")
            print(f"\nExporting to {format_ext}...")

            if export_document(service, document_id, format_ext, mime_type, output_path):
                successful_exports.append(format_ext)

        # For spreadsheets, also export all sheets as individual CSV files
        if doc_type == "spreadsheet":
            print("\n" + "-" * 50)
            export_all_sheets_as_csv(service, document_id, output_dir, doc_title)

        # Summary
        print("\n" + "=" * 50)
        print(f"Export complete! Successfully exported {len(successful_exports)}/{len(formats)} formats:")
        for fmt in successful_exports:
            print(f"  ✅ {fmt}")

        print(f"\nAll files saved in: {output_dir}/")

        # Special note about HTML for markdown conversion
        if "html" in successful_exports:
            print("\nNote: To convert to Markdown, you can use pandoc or html2text on the HTML export:")
            print(f"  pandoc {output_dir}/{safe_title}.html -o {output_dir}/{safe_title}.md")
            print(f"  html2text {output_dir}/{safe_title}.html > {output_dir}/{safe_title}.md")


if __name__ == "__main__":
    main()
