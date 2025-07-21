"""Google Drive document exporter utilities."""

import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qs, urlparse

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from loguru import logger
from pydantic import BaseModel, Field, field_validator


@dataclass
class DocumentConfig:
    """Configuration for a single document to mirror."""

    url: str
    document_id: str
    depth: int = 0
    comment: str = ""


class ExportFormat(BaseModel):
    """Represents an export format configuration."""

    extension: str
    mime_type: str
    description: str | None = None


class GoogleDriveExporterConfig(BaseModel):
    """Configuration for GoogleDriveExporter."""

    credentials_path: Path = Field(default=Path("tmp/credentials.json"))
    token_path: Path = Field(default=Path("tmp/token_drive.json"))
    target_directory: Path = Field(default=Path("exports"))
    export_format: Literal["pdf", "docx", "odt", "rtf", "txt", "html", "epub", "zip", "all"] = "html"
    link_depth: int = Field(default=0, ge=0, le=5)
    follow_links: bool = Field(default=False)
    scopes: list[str] = Field(
        default_factory=lambda: [
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/documents.readonly",
        ]
    )

    @field_validator("target_directory", mode="before")
    @classmethod
    def ensure_path(cls, v):
        """Ensure target_directory is a Path object."""
        return Path(v) if not isinstance(v, Path) else v


class GoogleDriveExporter:
    """Export Google Drive documents in various formats with link following capabilities."""

    EXPORT_FORMATS: dict[str, ExportFormat] = {
        "pdf": ExportFormat(extension="pdf", mime_type="application/pdf", description="Portable Document Format"),
        "docx": ExportFormat(
            extension="docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            description="Microsoft Word",
        ),
        "odt": ExportFormat(
            extension="odt", mime_type="application/vnd.oasis.opendocument.text", description="OpenDocument Text"
        ),
        "rtf": ExportFormat(extension="rtf", mime_type="application/rtf", description="Rich Text Format"),
        "txt": ExportFormat(extension="txt", mime_type="text/plain", description="Plain Text"),
        "html": ExportFormat(extension="html", mime_type="text/html", description="HTML Document"),
        "epub": ExportFormat(extension="epub", mime_type="application/epub+zip", description="EPUB eBook"),
        "zip": ExportFormat(extension="zip", mime_type="application/zip", description="HTML Zipped"),
    }

    def __init__(self, config: GoogleDriveExporterConfig | None = None):
        """Initialize the exporter with configuration.

        Args:
            config: Configuration object. If None, uses defaults.
        """
        self.config = config or GoogleDriveExporterConfig()
        self._service = None
        self._processed_docs: set[str] = set()

    @property
    def service(self):
        """Get or create the Google Drive service instance."""
        if self._service is None:
            creds = self._authenticate()
            self._service = build("drive", "v3", credentials=creds)
        return self._service

    def _authenticate(self) -> Credentials:
        """Authenticate with Google Drive API.

        Returns:
            Authenticated credentials.
        """
        creds = None

        if self.config.token_path.exists():
            logger.debug(f"Loading credentials from {self.config.token_path}")
            creds = Credentials.from_authorized_user_file(str(self.config.token_path), self.config.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(google.auth.transport.requests.Request())
            else:
                if not self.config.credentials_path.exists():
                    raise FileNotFoundError(f"Credentials file not found: {self.config.credentials_path}")

                logger.info("Running OAuth flow for new credentials")
                flow = InstalledAppFlow.from_client_secrets_file(str(self.config.credentials_path), self.config.scopes)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            self.config.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.token_path, "w") as token:
                token.write(creds.to_json())

        return creds

    def get_authenticated_user_info(self) -> dict:
        """Get information about the currently authenticated user.

        Returns:
            User information dictionary.
        """
        try:
            # Use the 'about' endpoint to get user info
            about = self.service.about().get(fields="user").execute()
            user_info: dict[Any, Any] = about.get("user", {})
            return user_info
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {}

    def extract_document_id(self, url_or_id: str) -> str:
        """Extract document ID from URL or return the ID if already provided.

        Args:
            url_or_id: Google Docs URL or document ID.

        Returns:
            Document ID.
        """
        # If it looks like a URL
        if url_or_id.startswith(("http://", "https://")):
            # Match various Google Doc URL patterns (including tab parameters)
            patterns = [
                r"/document/d/([a-zA-Z0-9-_]+)",
                r"/document/u/\d+/d/([a-zA-Z0-9-_]+)",
                r"/open\?id=([a-zA-Z0-9-_]+)",
                r"id=([a-zA-Z0-9-_]+)",
            ]

            for pattern in patterns:
                match = re.search(pattern, url_or_id)
                if match:
                    return match.group(1)

            # Try parsing as URL
            parsed = urlparse(url_or_id)
            if parsed.query:
                params = parse_qs(parsed.query)
                if "id" in params:
                    return params["id"][0]

            raise ValueError(f"Could not extract document ID from URL: {url_or_id}")

        # Assume it's already a document ID
        return url_or_id

    def parse_config_file(self, config_path: Path) -> list[DocumentConfig]:
        """Parse the mirror configuration file.

        Args:
            config_path: Path to the configuration file.

        Returns:
            List of DocumentConfig objects.

        Format:
            # Comments start with #
            # Format: URL [depth=N] [# comment]
            https://docs.google.com/document/d/ID/edit depth=2 # Optional comment
            https://docs.google.com/document/d/ID/edit # Uses default depth=0
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        documents = []

        try:
            with open(config_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Parse the line
                    try:
                        doc_config = self._parse_config_line(line)
                        documents.append(doc_config)
                        logger.debug(f"Parsed document: {doc_config.document_id} (depth={doc_config.depth})")
                    except Exception as e:
                        logger.error(f"Error parsing line {line_num}: {line} - {e}")
                        continue

        except Exception as e:
            logger.error(f"Error reading configuration file {config_path}: {e}")
            raise

        logger.info(f"Loaded {len(documents)} documents from {config_path}")
        return documents

    def _parse_config_line(self, line: str) -> DocumentConfig:
        """Parse a single configuration line.

        Args:
            line: Configuration line to parse.

        Returns:
            DocumentConfig object.
        """
        # Split by # to separate URL/params from comment
        parts = line.split("#", 1)
        url_part = parts[0].strip()
        comment = parts[1].strip() if len(parts) > 1 else ""

        # Parse depth parameter
        depth = 0
        if "depth=" in url_part:
            # Extract depth parameter
            url_tokens = url_part.split()
            url = url_tokens[0]

            for token in url_tokens[1:]:
                if token.startswith("depth="):
                    try:
                        depth = int(token.split("=", 1)[1])
                    except ValueError:
                        logger.warning(f"Invalid depth value: {token}")
                    break
        else:
            # No depth parameter, use the whole thing as URL
            url = url_part

        # Extract document ID
        document_id = self.extract_document_id(url)

        return DocumentConfig(url=url, document_id=document_id, depth=depth, comment=comment)

    def get_document_metadata(self, document_id: str) -> dict:
        """Get metadata for a document using multiple fallback methods.

        Args:
            document_id: Google Drive document ID.

        Returns:
            Document metadata including name and mime type.
        """
        # Method 1: Try Drive API first
        try:
            file_metadata = (
                self.service.files()
                .get(fileId=document_id, fields="name,mimeType,modifiedTime,owners,createdTime")
                .execute()
            )
            logger.debug(f"Got metadata via Drive API: {file_metadata.get('name')}")
            metadata: dict[Any, Any] = file_metadata
            return metadata
        except HttpError as drive_error:
            logger.debug(f"Drive API failed: {drive_error}")

            # Method 2: Try Google Docs API as fallback
            if drive_error.resp.status == 404:
                try:
                    logger.debug("Trying Google Docs API fallback...")

                    # Create Docs service if we don't have one
                    if not hasattr(self, "_docs_service"):
                        creds = self._authenticate()
                        self._docs_service = build("docs", "v1", credentials=creds)

                    # Get document via Docs API
                    doc = self._docs_service.documents().get(documentId=document_id).execute()

                    # Create metadata dict similar to Drive API response
                    docs_metadata = {
                        "name": doc.get("title", "untitled"),
                        "mimeType": "application/vnd.google-apps.document",
                        "modifiedTime": doc.get("revisionId"),  # Not the same, but something
                        "owners": [],  # Not available via Docs API
                        "createdTime": None,  # Not available via Docs API
                    }

                    logger.info(f"Got metadata via Docs API fallback: {docs_metadata.get('name')}")
                    return docs_metadata

                except Exception as docs_error:
                    logger.debug(f"Docs API fallback also failed: {docs_error}")
                    # Fall through to original error handling

            # Original error handling if all methods fail
            if drive_error.resp.status == 404:
                logger.error(f"Document not found or not accessible: {document_id}")
                logger.error("This could mean:")
                logger.error("1. Document is not shared with your OAuth account")
                logger.error("2. Document doesn't exist or was deleted")
                logger.error("3. You're using a different Google account in your browser")
                logger.error(f"Document URL: https://docs.google.com/document/d/{document_id}/edit")
            elif drive_error.resp.status == 403:
                logger.error(f"Permission denied for document: {document_id}")
                logger.error("The document exists but you don't have access permissions")
            else:
                logger.error(f"Failed to get document metadata: {drive_error}")
            raise

    def _export_single_format(self, document_id: str, format_key: str, output_path: Path) -> bool:
        """Export document in a single format.

        Args:
            document_id: Google Drive document ID.
            format_key: Format key from EXPORT_FORMATS.
            output_path: Path to save the exported file.

        Returns:
            True if export successful, False otherwise.
        """
        if format_key not in self.EXPORT_FORMATS:
            logger.error(f"Unknown format: {format_key}")
            return False

        export_format = self.EXPORT_FORMATS[format_key]

        try:
            request = self.service.files().export_media(fileId=document_id, mimeType=export_format.mime_type)

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.debug(f"Download progress: {progress}%")

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(output_path, "wb") as f:
                f.write(fh.getvalue())

            logger.success(f"Exported to {output_path}")
            return True

        except HttpError as error:
            logger.error(f"Failed to export {format_key}: {error}")
            return False

    def _extract_links_from_html(self, html_path: Path) -> list[str]:
        """Extract Google Drive links from exported HTML.

        Args:
            html_path: Path to the HTML file.

        Returns:
            List of Google Drive document IDs found in the HTML.
        """
        if not html_path.exists():
            return []

        try:
            with open(html_path, encoding="utf-8") as f:
                content = f.read()

            # Find all Google Docs/Drive links (including wrapped redirect URLs)
            patterns = [
                # Direct Google Docs/Drive links
                r'href="https://(?:docs\.google\.com/document/(?:u/\d+/)?d/|drive\.google\.com/file/d/|drive\.google\.com/open\?id=)([a-zA-Z0-9-_]+)',
                # Google-wrapped redirect URLs containing docs.google.com
                r'href="https://www\.google\.com/url\?q=https://docs\.google\.com/document/(?:u/\d+/)?d/([a-zA-Z0-9-_]+)',
                # Google-wrapped redirect URLs with drive.google.com
                r'href="https://www\.google\.com/url\?q=https://drive\.google\.com/(?:file/d/|open\?id=)([a-zA-Z0-9-_]+)',
            ]

            all_matches = []
            for pattern in patterns:
                matches = re.findall(pattern, content)
                all_matches.extend(matches)

            logger.debug(f"Found {len(all_matches)} potential Google Drive links")

            # Remove duplicates while preserving order
            seen = set()
            unique_ids = []
            for doc_id in all_matches:
                if doc_id not in seen and doc_id not in self._processed_docs:
                    seen.add(doc_id)
                    unique_ids.append(doc_id)
                    logger.debug(f"Added document ID to process: {doc_id}")

            return unique_ids

        except Exception as e:
            logger.error(f"Failed to extract links from {html_path}: {e}")
            return []

    def export_document(
        self, document_id: str, output_name: str | None = None, current_depth: int = 0
    ) -> dict[str, Path]:
        """Export a Google Drive document.

        Args:
            document_id: Google Drive document ID or URL.
            output_name: Optional custom output name (without extension).
            current_depth: Current recursion depth for link following.

        Returns:
            Dictionary mapping format names to output paths.
        """
        document_id = self.extract_document_id(document_id)

        if document_id in self._processed_docs:
            logger.info(f"Document {document_id} already processed, skipping")
            return {}

        self._processed_docs.add(document_id)

        # Get document metadata (non-fatal if it fails)
        doc_title = "untitled"
        try:
            metadata = self.get_document_metadata(document_id)
            doc_title = metadata.get("name", "untitled")
        except Exception as e:
            logger.warning(f"Could not get metadata for {document_id}, using 'untitled': {e}")
            # Continue with export even if metadata fails

        safe_title = output_name or re.sub(r"[^\w\s-]", "_", doc_title).strip()

        # Ensure target directory exists
        self.config.target_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting '{doc_title}' (ID: {document_id}) to {self.config.target_directory}")

        # Determine formats to export
        formats_to_export = []
        if self.config.export_format == "all":
            formats_to_export = list(self.EXPORT_FORMATS.keys())
        else:
            formats_to_export = [self.config.export_format]

        # If following links, we need HTML format for link extraction
        # Add it if not already present and we're configured to follow links
        if self.config.follow_links and current_depth < self.config.link_depth and "html" not in formats_to_export:
            formats_to_export.append("html")
            logger.debug("Added HTML format for link extraction")

        # Export document - files go directly in target directory
        exported_files = {}
        for format_key in formats_to_export:
            export_format = self.EXPORT_FORMATS[format_key]

            # Create filename - always use clean title for primary export
            base_filename = safe_title
            output_path = self.config.target_directory / f"{base_filename}.{export_format.extension}"

            # If file exists, just overwrite it (mirror behavior should update existing files)
            # This handles the common case where we're re-running a mirror operation

            if self._export_single_format(document_id, format_key, output_path):
                exported_files[format_key] = output_path

        # Process linked documents if requested
        if self.config.follow_links and current_depth < self.config.link_depth and "html" in exported_files:
            logger.info(f"Searching for linked documents (depth {current_depth + 1}/{self.config.link_depth})")
            linked_ids = self._extract_links_from_html(exported_files["html"])

            if linked_ids:
                logger.info(f"Found {len(linked_ids)} linked documents")
                for linked_id in linked_ids:
                    try:
                        self.export_document(linked_id, current_depth=current_depth + 1)
                    except Exception as e:
                        logger.error(f"Failed to export linked document {linked_id}: {e}")

        return exported_files

    def export_multiple(self, document_ids: list[str]) -> dict[str, dict[str, Path]]:
        """Export multiple documents.

        Args:
            document_ids: List of document IDs or URLs.

        Returns:
            Dictionary mapping document IDs to their exported file paths.
        """
        results = {}

        for doc_id in document_ids:
            try:
                extracted_id = self.extract_document_id(doc_id)
                exported = self.export_document(doc_id)
                if exported:
                    results[extracted_id] = exported
            except Exception as e:
                logger.error(f"Failed to export {doc_id}: {e}")

        return results

    def mirror_documents(self, config_path: Path) -> dict[str, dict[str, Path]]:
        """Mirror documents from a configuration file.

        Args:
            config_path: Path to the configuration file.

        Returns:
            Dictionary mapping document IDs to their exported file paths.
        """
        # Parse configuration file
        documents = self.parse_config_file(config_path)

        if not documents:
            logger.warning("No documents found in configuration file")
            return {}

        logger.info(f"Starting mirror of {len(documents)} documents")

        results = {}

        # Process each document with its specific depth setting
        for doc_config in documents:
            try:
                logger.info(f"Mirroring '{doc_config.comment or doc_config.document_id}' (depth={doc_config.depth})")

                # Temporarily override link depth for this specific document
                original_follow_links = self.config.follow_links
                original_link_depth = self.config.link_depth

                # Set follow_links based on whether depth > 0
                self.config.follow_links = doc_config.depth > 0
                self.config.link_depth = doc_config.depth

                try:
                    exported = self.export_document(doc_config.document_id)
                    if exported:
                        results[doc_config.document_id] = exported
                finally:
                    # Restore original settings
                    self.config.follow_links = original_follow_links
                    self.config.link_depth = original_link_depth

            except Exception as e:
                logger.error(f"Failed to mirror document {doc_config.document_id}: {e}")
                continue

        logger.info(f"Mirror completed: {len(results)}/{len(documents)} documents exported")
        return results
