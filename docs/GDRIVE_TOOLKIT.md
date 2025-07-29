# Google Drive Toolkit

The Google Drive Toolkit provides AI agents with the ability to download and manage Google Drive documents (Docs, Sheets, Slides) in various formats.

## Features

- Download Google Docs, Sheets, and Slides documents
- Support for multiple export formats (PDF, DOCX, HTML, Markdown, CSV, etc.)
- Automatic format detection based on document type
- Batch downloading of multiple documents
- Integration with workspace directory management
- OAuth authentication with Google Drive API

## Setup

### 1. Google Drive API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Create OAuth 2.0 credentials for a desktop application
5. Download the credentials JSON file
6. Place it in your project root as `.client_secret.googleusercontent.com.json`

### 2. Dependencies

The toolkit requires these additional dependencies:
```bash
uv add google-auth google-auth-oauthlib google-api-python-client html-to-markdown
```

## Usage

### Basic Usage

```python
from pathlib import Path
from agno.agent import Agent
from sidekick.tools import GoogleDriveTools

# Initialize the toolkit
gdrive_tools = GoogleDriveTools(
    workspace_dir=Path("./workspace"),  # Where to save downloads
    credentials_path=Path(".client_secret.googleusercontent.com.json")
)

# Create an agent
agent = Agent(tools=[gdrive_tools], show_tool_calls=True)

# Use natural language commands (defaults to markdown format for Google Docs)
response = agent.run("Download this Google Doc: https://docs.google.com/document/d/YOUR_DOC_ID/edit")
```

### Supported Commands

The toolkit responds to natural language commands such as:

- **Download single document**: "Download this document: [URL]" (defaults to markdown for Google Docs)
- **Download with specific format**: "Download this document as PDF: [URL]"
- **Download multiple documents**: "Download these 3 documents: [URL1], [URL2], [URL3]" (defaults to markdown)
- **List formats**: "What export formats are supported for spreadsheets?"
- **Get user info**: "Who is the currently authenticated Google Drive user?"
- **Extract document ID**: "What's the document ID from this URL: [URL]"

### Supported Export Formats

#### Google Documents
- `pdf` - Portable Document Format
- `docx` - Microsoft Word
- `odt` - OpenDocument Text
- `rtf` - Rich Text Format
- `txt` - Plain Text
- `html` - HTML Document
- `epub` - EPUB eBook
- `zip` - HTML Zipped
- `md` - Markdown Document

#### Google Sheets
- `pdf` - Portable Document Format
- `xlsx` - Microsoft Excel
- `ods` - OpenDocument Spreadsheet
- `csv` - Comma-Separated Values
- `tsv` - Tab-Separated Values
- `zip` - HTML Zipped

#### Google Slides
- `pptx` - Microsoft PowerPoint
- `odp` - OpenDocument Presentation
- `pdf` - Portable Document Format
- `txt` - Plain Text
- `html` - HTML Document

## Tool Functions

The toolkit provides these functions to AI agents:

### `download_document(url_or_id, format="md", output_name=None)`
Downloads a single Google Drive document.

**Parameters:**
- `url_or_id`: Google Drive URL or document ID
- `format`: Export format (default: "md" for markdown)
- `output_name`: Optional custom output name (without extension)

### `download_multiple_documents(urls_or_ids, format="md")`
Downloads multiple Google Drive documents.

**Parameters:**
- `urls_or_ids`: List of Google Drive URLs or document IDs
- `format`: Export format for all documents (default: "md" for markdown)

### `list_supported_formats(document_type="document")`
Lists supported export formats for different document types.

**Parameters:**
- `document_type`: "document", "spreadsheet", or "presentation"

### `get_user_info()`
Gets information about the currently authenticated Google user.

### `extract_document_id(url)`
Extracts document ID from a Google Drive URL.

**Parameters:**
- `url`: Google Drive URL

## File Organization

Downloaded files are saved to the workspace directory with the following structure:
```
workspace/
├── Document_Name.pdf
├── Spreadsheet_Name.xlsx
└── Presentation_Name.pptx
```

## Authentication Flow

On first use, the toolkit will:
1. Open a browser window for Google OAuth authentication
2. Ask you to sign in and grant permissions
3. Save authentication tokens for future use
4. The token is saved to `tmp/token_drive.json`

## Error Handling

The toolkit handles common errors:
- Document not found or not accessible
- Unsupported format combinations
- Authentication failures
- Network connectivity issues

All errors are logged and returned as descriptive messages to the AI agent.

## Example

See `examples/gdrive_example.py` for a complete working example.

## Security Notes

- Keep your credentials file secure and never commit it to version control
- The toolkit only requests necessary permissions for document access
- Authentication tokens are stored locally and encrypted
- All downloads respect Google Drive sharing permissions
