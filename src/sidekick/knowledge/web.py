"""Web page knowledge source implementation."""

import asyncio
import fnmatch
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler
from loguru import logger

from .base import DownloadResult, KnowledgeSource
from .config import WebSourceConfig


class WebSource(KnowledgeSource):
    """Web page knowledge source using crawl4ai."""

    def __init__(self, config: WebSourceConfig, base_path: Path | None = None):
        """Initialize Web source.

        Args:
            config: Web source configuration
            base_path: Base path for knowledge storage
        """
        super().__init__(config, base_path)
        self.config: WebSourceConfig = config

    def download(self, **kwargs) -> DownloadResult:
        """Download web pages.

        Keyword Args:
            urls: List of URLs to download
            depth: Crawling depth

        Returns:
            DownloadResult with downloaded files
        """
        urls = kwargs.get("urls", self.config.urls)
        depth = kwargs.get("depth", self.config.depth)

        return asyncio.run(self._crawl_and_download_async(urls, depth))

    def sync(self, manifest: dict[str, Any] | None = None) -> DownloadResult:
        """Sync web pages based on configuration.

        Args:
            manifest: Previous manifest (not used for Web)

        Returns:
            DownloadResult with downloaded files
        """
        return asyncio.run(self._crawl_and_download_async(self.config.urls, self.config.depth))

    async def _crawl_and_download_async(self, start_urls: list[str], max_depth: int) -> DownloadResult:
        """Crawl and download web pages using crawl4ai.

        Args:
            start_urls: Starting URLs
            max_depth: Maximum crawling depth

        Returns:
            DownloadResult with downloaded files
        """
        result = DownloadResult(source_name=self.config.name)

        # Ensure output directory exists
        self.ensure_output_dir()

        downloaded_files = []

        try:
            logger.info(f"Starting web crawl with max_depth={max_depth}")
            logger.info(f"Start URLs: {start_urls}")
            if self.config.patterns:
                logger.info(f"URL patterns for filtering: {self.config.patterns}")
            else:
                logger.info("No URL patterns configured - will crawl all discovered links")

            async with AsyncWebCrawler(verbose=True) as crawler:
                if max_depth == 0:
                    # Simple crawling - just download the provided URLs
                    logger.info("Simple crawling mode (depth=0) - downloading only specified URLs")
                    for url in start_urls:
                        try:
                            logger.info(f"Crawling: {url}")
                            crawler_result = await crawler.arun(url=url)

                            if crawler_result.success:
                                file_path = await self._save_content(url, crawler_result)
                                if file_path:
                                    downloaded_files.append(file_path)
                                    logger.debug(f"Downloaded: {file_path.name}")
                            else:
                                error_message = getattr(crawler_result, "error_message", "Unknown")
                                error_msg = f"Failed to crawl {url}: {error_message}"
                                logger.error(error_msg)
                                result.errors.append(error_msg)

                        except Exception as e:
                            error_msg = f"Failed to crawl {url}: {e}"
                            logger.error(error_msg)
                            result.errors.append(error_msg)
                else:
                    # Deep crawling with specified depth
                    logger.info(f"Deep crawling mode (depth={max_depth}) - downloading URLs and following links")
                    for url in start_urls:
                        try:
                            logger.info(f"Deep crawling: {url}")

                            # For deep crawling, we'll crawl the main URL and then follow links
                            crawler_result = await crawler.arun(url=url)

                            if crawler_result.success:
                                file_path = await self._save_content(url, crawler_result)
                                if file_path:
                                    downloaded_files.append(file_path)
                                    logger.info(f"✓ Downloaded main page: {file_path.name}")

                                # Extract and follow links up to max_depth
                                if max_depth > 0:
                                    extracted_links = self._extract_links_from_content(url, crawler_result)
                                    logger.info(f"Found {len(extracted_links)} links on {url}")

                                    filtered_links = self._filter_links(extracted_links)
                                    logger.info(
                                        f"After pattern filtering: {len(filtered_links)} links match (downloading all)"
                                    )

                                    # Process all filtered links
                                    for i, link in enumerate(filtered_links, 1):
                                        try:
                                            logger.info(f"[{i}/{len(filtered_links)}] Crawling linked page: {link}")
                                            sub_result = await crawler.arun(url=link)
                                            if sub_result.success:
                                                sub_file_path = await self._save_content(link, sub_result)
                                                if sub_file_path:
                                                    downloaded_files.append(sub_file_path)
                                                    logger.info(f"✓ Downloaded: {sub_file_path.name}")
                                            else:
                                                error_message = getattr(sub_result, "error_message", "Unknown")
                                                logger.warning(f"✗ Failed to crawl {link}: {error_message}")
                                        except Exception as e:
                                            logger.warning(f"✗ Failed to crawl linked page {link}: {e}")

                            else:
                                error_message = getattr(crawler_result, "error_message", "Unknown")
                                error_msg = f"Failed to deep crawl {url}: {error_message}"
                                logger.error(error_msg)
                                result.errors.append(error_msg)

                        except Exception as e:
                            error_msg = f"Failed to deep crawl {url}: {e}"
                            logger.error(error_msg)
                            result.errors.append(error_msg)

            result.files_downloaded = downloaded_files
            logger.info(f"Downloaded {len(downloaded_files)} web pages")

        except Exception as e:
            error_msg = f"Web crawling failed: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            result.success = False

        # Set success based on whether we downloaded any files
        if result.success:
            result.success = len(result.files_downloaded) > 0

        return result

    async def _save_content(self, url: str, crawler_result) -> Path | None:
        """Save crawled content to file.

        Args:
            url: Original URL
            crawler_result: Crawl4ai result object

        Returns:
            Path to saved file or None if failed
        """
        try:
            # Generate filename from URL
            parsed_url = urlparse(url)
            filename = self._url_to_filename(parsed_url)
            file_path = self.output_dir / filename

            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if self.config.export_format == "md":
                # Use crawl4ai's built-in markdown conversion
                markdown_content = crawler_result.markdown or crawler_result.cleaned_html or ""

                # Add URL as metadata at the top
                content = f"# {parsed_url.netloc}{parsed_url.path}\n\nSource: {url}\n\n{markdown_content}"

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                # Save as HTML
                html_content = crawler_result.html or ""
                file_path = file_path.with_suffix(".html")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

            return file_path

        except Exception as e:
            logger.error(f"Failed to save content for {url}: {e}")
            return None

    def _extract_links_from_content(self, base_url: str, crawler_result) -> list[str]:
        """Extract links from crawl4ai result content.

        Args:
            base_url: Base URL for resolving relative links
            crawler_result: Crawl4ai result object

        Returns:
            List of absolute URLs
        """
        links = []

        try:
            # Extract links from the crawler result
            if hasattr(crawler_result, "links") and crawler_result.links:
                # crawl4ai returns links as dict with 'internal' and 'external' keys
                if isinstance(crawler_result.links, dict):
                    # Process internal links
                    internal_links = crawler_result.links.get("internal", [])
                    for link_data in internal_links:
                        if isinstance(link_data, dict) and "href" in link_data:
                            href = link_data["href"]
                            if href and not href.startswith("#") and href.startswith(("http://", "https://")):
                                links.append(href)

                    # Process external links if needed
                    external_links = crawler_result.links.get("external", [])
                    for link_data in external_links:
                        if isinstance(link_data, dict) and "href" in link_data:
                            href = link_data["href"]
                            if href and not href.startswith("#") and href.startswith(("http://", "https://")):
                                links.append(href)
                else:
                    # Fallback for different link structure
                    for link_data in crawler_result.links:
                        href = (
                            link_data["href"] if isinstance(link_data, dict) and "href" in link_data else str(link_data)
                        )

                        # Skip empty links and anchors
                        if not href or href.startswith("#"):
                            continue

                        # Convert relative URLs to absolute
                        absolute_url = urljoin(base_url, href)

                        # Basic URL validation
                        if absolute_url.startswith(("http://", "https://")):
                            links.append(absolute_url)

            # Fallback: extract from HTML if links attribute not available
            elif hasattr(crawler_result, "html") and crawler_result.html:
                href_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>'
                matches = re.findall(href_pattern, crawler_result.html, re.IGNORECASE)

                for href in matches:
                    if not href or href.startswith("#"):
                        continue

                    absolute_url = urljoin(base_url, href)

                    if absolute_url.startswith(("http://", "https://")):
                        links.append(absolute_url)

        except Exception as e:
            logger.error(f"Failed to extract links from crawler result: {e}")

        return links

    def _filter_links(self, links: list[str]) -> list[str]:
        """Filter links based on configuration patterns.

        Args:
            links: List of URLs to filter

        Returns:
            Filtered list of URLs
        """
        if not self.config.patterns:
            return links

        filtered = []
        for link in links:
            # Check if link matches any pattern using glob-style matching
            for pattern in self.config.patterns:
                if fnmatch.fnmatch(link, pattern):
                    filtered.append(link)
                    break

        return filtered

    def _url_to_filename(self, parsed_url) -> str:
        """Convert URL to a safe filename.

        Args:
            parsed_url: Parsed URL object

        Returns:
            Safe filename string
        """
        # Use path or default to index
        path = parsed_url.path.strip("/") or "index"

        # Replace path separators and invalid characters
        filename = re.sub(r"[^\w\-.]", "_", path.replace("/", "_"))

        # Add extension based on export format
        filename = f"{filename}.md" if self.config.export_format == "md" else f"{filename}.html"

        # Limit filename length
        if len(filename) > 100:
            name, ext = filename.rsplit(".", 1)
            filename = f"{name[:90]}...{ext}"

        return filename
