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
# Scopes for Google Drive API (read-only access)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/drive.metadata.readonly"]

# Available export formats for Google Docs
EXPORT_FORMATS = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "odt": "application/vnd.oasis.opendocument.text",
    "rtf": "application/rtf",
    "txt": "text/plain",
    "html": "text/html",
    "epub": "application/epub+zip",
    "zip": "application/zip",  # HTML zipped
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

    # Method 1: Standard files().get() API
    try:
        print("Trying Method 1: files().get() API...")
        file = service.files().get(fileId=file_id, fields="name").execute()
        title = file.get("name", "untitled")
        print(f"✅ Method 1 Success: {title}")
        return title
    except Exception as e:
        print(f"❌ Method 1 Failed: {e}")

    # Method 2: Try with different fields
    try:
        print("Trying Method 2: files().get() with minimal fields...")
        file = service.files().get(fileId=file_id, fields="id,name").execute()
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

    # Method 5: Try with different scope/permissions
    try:
        print("Trying Method 5: files().get() with supportsAllDrives=True...")
        file = service.files().get(fileId=file_id, fields="name", supportsAllDrives=True).execute()
        title = file.get("name", "untitled")
        print(f"✅ Method 5 Success: {title}")
        return title
    except Exception as e:
        print(f"❌ Method 5 Failed: {e}")

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


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_gdoc_all_formats.py <DOCUMENT_ID>")
        print("\nWhat is a Google Doc ID?")
        print("The Document ID is the long string in the Google Docs URL.")
        print("For example, in this URL:")
        print("https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit")
        print("The Document ID is: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
        print("\nThis script will export the document to all available formats:")
        for fmt, _mime in EXPORT_FORMATS.items():
            print(f"  - {fmt}")
        sys.exit(1)

    document_id = sys.argv[1].strip()
    print(f"Authenticating and fetching Google Doc with ID: {document_id}")

    # Authenticate and build service
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    # Get document title for naming files
    doc_title = get_document_title(service, document_id)
    safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in doc_title)

    # Create output directory
    output_dir = f"exports_{safe_title}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nExporting '{doc_title}' to directory: {output_dir}/")

    # Export to all formats
    print("\nExporting to all formats:")
    successful_exports = []

    for format_ext, mime_type in EXPORT_FORMATS.items():
        output_path = os.path.join(output_dir, f"{safe_title}.{format_ext}")
        print(f"\nExporting to {format_ext}...")

        if export_document(service, document_id, format_ext, mime_type, output_path):
            successful_exports.append(format_ext)

    # Summary
    print("\n" + "=" * 50)
    print(f"Export complete! Successfully exported {len(successful_exports)}/{len(EXPORT_FORMATS)} formats:")
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
