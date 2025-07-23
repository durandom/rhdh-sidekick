"""Google Drive knowledge source implementation."""

from pathlib import Path
from typing import Any

from loguru import logger

from ..utils.gdrive import GoogleDriveExporter, GoogleDriveExporterConfig
from .base import DownloadResult, KnowledgeSource
from .config import GDriveSourceConfig


class GDriveSource(KnowledgeSource):
    """Google Drive knowledge source."""

    def __init__(self, config: GDriveSourceConfig, base_path: Path | None = None):
        """Initialize Google Drive source.

        Args:
            config: Google Drive source configuration
            base_path: Base path for knowledge storage
        """
        super().__init__(config, base_path)
        self.config: GDriveSourceConfig = config

        # Create exporter config
        self.exporter_config = GoogleDriveExporterConfig(
            target_directory=self.output_dir,
            export_format=config.export_format,  # type: ignore[arg-type]
        )

    def download(self, **kwargs) -> DownloadResult:
        """Download Google Drive documents.

        Keyword Args:
            documents: List of document IDs or URLs
            depth: Depth for following links
            format: Export format

        Returns:
            DownloadResult with downloaded files
        """
        documents = kwargs.get("documents", [])
        depth = kwargs.get("depth", 0)
        format = kwargs.get("format", self.config.export_format)

        result = DownloadResult(source_name=self.config.name)

        try:
            # Update exporter config
            self.exporter_config.export_format = format
            self.exporter_config.link_depth = depth
            self.exporter_config.follow_links = depth > 0

            # Callback to track all downloaded files (including linked documents)
            def download_callback(document_id: str, format_key: str, output_path: Path, success: bool):
                if success and output_path.exists():
                    result.files_downloaded.append(output_path)
                    logger.debug(f"Tracked download: {output_path.name} (doc: {document_id}, format: {format_key})")

            # Create exporter with callback
            exporter = GoogleDriveExporter(self.exporter_config, download_callback=download_callback)

            # Download documents (callback will track all downloads)
            logger.info(f"Downloading {len(documents)} Google Drive documents")
            exporter.export_multiple(documents)

            logger.info(f"Downloaded {len(result.files_downloaded)} files from Google Drive")

        except Exception as e:
            logger.error(f"Failed to download from Google Drive: {e}")
            result.errors.append(str(e))
            result.success = False

        return result

    def sync(self, manifest: dict[str, Any] | None = None) -> DownloadResult:
        """Sync Google Drive documents based on configuration.

        Args:
            manifest: Previous manifest (not used for Google Drive)

        Returns:
            DownloadResult with downloaded files
        """
        result = DownloadResult(source_name=self.config.name)

        try:
            # Update exporter config for each document's depth settings
            max_depth = max((doc.get("depth", 0) for doc in self.config.documents), default=0)
            self.exporter_config.link_depth = max_depth
            self.exporter_config.follow_links = max_depth > 0

            # Callback to track all downloaded files (including linked documents)
            def download_callback(document_id: str, format_key: str, output_path: Path, success: bool):
                if success and output_path.exists():
                    result.files_downloaded.append(output_path)
                    logger.debug(f"Tracked download: {output_path.name} (doc: {document_id}, format: {format_key})")

            # Create exporter with callback
            exporter = GoogleDriveExporter(self.exporter_config, download_callback=download_callback)

            # Process each document with its specific settings
            for doc_config in self.config.documents:
                url = doc_config["url"]
                depth = doc_config.get("depth", 0)

                logger.debug(f"Processing document: {url} (depth={depth})")

                # Extract document ID
                doc_id = exporter.extract_document_id(url)

                # Set depth for this specific document
                self.exporter_config.link_depth = depth
                self.exporter_config.follow_links = depth > 0

                # Re-create exporter with updated config and same callback
                exporter = GoogleDriveExporter(self.exporter_config, download_callback=download_callback)

                # Export this document (callback will track all downloads)
                try:
                    exporter.export_multiple([doc_id])
                    files_count = len([f for f in result.files_downloaded])
                    logger.debug(f"Export completed for {url}, tracked {files_count} total files so far")

                except Exception as e:
                    error_msg = f"Failed to export {url}: {e}"
                    logger.error(error_msg)
                    result.errors.append(error_msg)

            logger.info(f"Synced {len(result.files_downloaded)} files from Google Drive")

            # Set success based on whether we got any files and no critical errors
            result.success = len(result.files_downloaded) > 0 or len(self.config.documents) == 0

        except Exception as e:
            logger.error(f"Failed to sync Google Drive: {e}")
            result.errors.append(str(e))
            result.success = False

        return result
