"""Knowledge management CLI commands."""

from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from ..knowledge.config import KnowledgeConfig
from ..knowledge.manifest import ManifestManager

console = Console()

# Create the knowledge sub-application
knowledge_app = typer.Typer(
    name="knowledge",
    help="Knowledge management commands for syncing documentation from various sources",
    rich_markup_mode="rich",
)

# Create sub-command for download
download_app = typer.Typer(
    name="download",
    help="Download content from various sources",
    rich_markup_mode="rich",
)
knowledge_app.add_typer(download_app, name="download")


@knowledge_app.command()
def sync(
    source: str | None = typer.Option(None, "--source", "-s", help="Sync specific source by name"),
    config_file: Path = typer.Option(
        Path("knowledge/external/sources.yaml"), "--config", "-c", help="Path to configuration file"
    ),
    base_path: Path = typer.Option(
        Path("knowledge/external"), "--base-path", "-b", help="Base path for knowledge storage"
    ),
):
    """Sync knowledge sources from configuration file.

    This command reads the configuration file and syncs all configured sources.
    Files that were previously downloaded but are no longer available will be removed.

    Examples:
        # Sync all sources (uses knowledge/external/sources.yaml → knowledge/external/ by default)
        sidekick knowledge sync

        # Sync specific source
        sidekick knowledge sync --source gdrive

        # Use custom config file and output path
        sidekick knowledge sync --config my-sources.yaml --base-path knowledge/my-project
    """
    try:
        # Load configuration
        config = KnowledgeConfig.load_from_file(config_file)
        manifest_manager = ManifestManager(base_path)

        # Filter sources if specific source requested
        sources_to_sync = config.sources
        if source:
            source_config = config.get_source_by_name(source)
            if not source_config:
                console.print(f"[red]✗ Source '{source}' not found in configuration[/red]")
                raise typer.Exit(1) from None
            sources_to_sync = [source_config]

        console.print(f"[bold blue]Syncing {len(sources_to_sync)} source(s)...[/bold blue]")

        # Track results
        total_downloaded = 0
        total_removed = 0
        errors = []

        # Sync each source
        for source_config in sources_to_sync:
            console.print(f"\n[cyan]Syncing {source_config.name} ({source_config.type})...[/cyan]")

            try:
                # Import and create appropriate source handler
                source_handler: Any
                if source_config.type == "gdrive":
                    from ..knowledge.gdrive import GDriveSource

                    source_handler = GDriveSource(source_config, base_path)
                elif source_config.type == "git":
                    from ..knowledge.git import GitSource

                    source_handler = GitSource(source_config, base_path)
                elif source_config.type == "web":
                    from ..knowledge.web import WebSource

                    source_handler = WebSource(source_config, base_path)
                else:
                    console.print(f"[red]✗ Unknown source type: {source_config.type}[/red]")  # type: ignore[unreachable]
                    continue

                # Get previous manifest
                manifest = manifest_manager.get_manifest(source_config.name)

                # Sync the source
                result = source_handler.sync(manifest=manifest.model_dump() if manifest else None)

                if result.success:
                    # Handle cleanup
                    removed_files = manifest_manager.sync_and_cleanup(source_config.name, result.files_downloaded)

                    total_downloaded += len(result.files_downloaded)
                    total_removed += len(removed_files)

                    console.print(
                        f"[green]✓ {source_config.name}: "
                        f"{len(result.files_downloaded)} files downloaded, "
                        f"{len(removed_files)} files removed[/green]"
                    )
                else:
                    errors.extend(result.errors)
                    console.print(f"[red]✗ {source_config.name}: Failed to sync[/red]")
                    for error in result.errors:
                        console.print(f"  [red]{error}[/red]")

            except ImportError:
                error_msg = f"{source_config.name}: Source type {source_config.type} not implemented yet"
                errors.append(error_msg)
                console.print(f"[yellow]⚠ {error_msg}[/yellow]")
            except Exception as e:
                error_msg = f"{source_config.name}: {str(e)}"
                errors.append(error_msg)
                console.print(f"[red]✗ {error_msg}[/red]")

        # Summary
        console.print("\n[bold]Sync Summary:[/bold]")
        console.print(f"  Total files downloaded: {total_downloaded}")
        console.print(f"  Total files removed: {total_removed}")
        if errors:
            console.print(f"  [red]Errors: {len(errors)}[/red]")
        else:
            console.print("  [green]No errors[/green]")

    except FileNotFoundError:
        console.print(f"[red]✗ Configuration file not found: {config_file}[/red]")
        console.print("[dim]Create a sources.yaml file with your knowledge sources[/dim]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗ Sync failed: {e}[/red]")
        raise typer.Exit(1) from None


@download_app.command("gdrive")
def download_gdrive(
    documents: list[str] = typer.Argument(..., help="Google Drive document IDs or URLs"),
    output: Path = typer.Option(Path("knowledge/gdrive-download"), "--output", "-o", help="Output directory"),
    depth: int = typer.Option(0, "--depth", "-d", help="Depth for following links (0-5)"),
    format: str = typer.Option("md", "--format", "-f", help="Export format (md, pdf, docx, html, etc.)"),
):
    """Download Google Drive documents.

    Examples:
        # Download single document
        sidekick knowledge download gdrive "https://docs.google.com/document/d/ID/edit"

        # Download with link following
        sidekick knowledge download gdrive doc_id --depth 2

        # Download multiple documents
        sidekick knowledge download gdrive doc_id1 doc_id2 doc_id3
    """
    try:
        from ..knowledge.config import GDriveSourceConfig
        from ..knowledge.gdrive import GDriveSource

        # Create temporary config
        doc_configs = [{"url": doc, "depth": depth if i == 0 else 0} for i, doc in enumerate(documents)]

        config = GDriveSourceConfig(name="gdrive-download", documents=doc_configs, export_format=format)

        source = GDriveSource(config, output.parent)
        source.output_dir = output  # Override output directory

        console.print(f"[bold blue]Downloading {len(documents)} document(s) to {output}...[/bold blue]")

        result = source.download(documents=documents, depth=depth, format=format)

        if result.success:
            console.print(f"[green]✓ Downloaded {len(result.files_downloaded)} files[/green]")
        else:
            console.print("[red]✗ Download failed[/red]")
            for error in result.errors:
                console.print(f"  [red]{error}[/red]")
            raise typer.Exit(1) from None

    except ImportError:
        console.print("[red]✗ Google Drive source not implemented yet[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗ Download failed: {e}[/red]")
        raise typer.Exit(1) from None


@download_app.command("git")
def download_git(
    url: str = typer.Argument(..., help="Git repository URL"),
    output: Path = typer.Option(Path("knowledge/git-download"), "--output", "-o", help="Output directory"),
    branch: str = typer.Option("main", "--branch", "-b", help="Branch to checkout"),
    files: list[str] = typer.Option(["**/*.md", "README.md"], "--files", "-f", help="File patterns to copy"),
):
    """Download files from a git repository.

    Examples:
        # Clone and extract markdown files
        sidekick knowledge download git "https://github.com/org/repo"

        # Specify branch and file patterns
        sidekick knowledge download git "https://github.com/org/repo" --branch develop --files "docs/**/*.md"
    """
    try:
        from ..knowledge.config import GitSourceConfig
        from ..knowledge.git import GitSource

        # Create temporary config
        config = GitSourceConfig(name="git-download", url=url, branch=branch, files=files)

        source = GitSource(config, output.parent)
        source.output_dir = output  # Override output directory

        console.print(f"[bold blue]Downloading from {url} ({branch}) to {output}...[/bold blue]")

        result = source.download(url=url, branch=branch, files=files)

        if result.success:
            console.print(f"[green]✓ Downloaded {len(result.files_downloaded)} files[/green]")
        else:
            console.print("[red]✗ Download failed[/red]")
            for error in result.errors:
                console.print(f"  [red]{error}[/red]")
            raise typer.Exit(1) from None

    except ImportError:
        console.print("[red]✗ Git source not implemented yet[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗ Download failed: {e}[/red]")
        raise typer.Exit(1) from None


@download_app.command("web")
def download_web(
    urls: list[str] = typer.Argument(..., help="Web page URLs"),
    output: Path = typer.Option(Path("knowledge/web-download"), "--output", "-o", help="Output directory"),
    depth: int = typer.Option(1, "--depth", "-d", help="Crawling depth (0-5)"),
):
    """Download web pages.

    Examples:
        # Download single page
        sidekick knowledge download web "https://example.com/docs"

        # Download with crawling
        sidekick knowledge download web "https://example.com/docs" --depth 2

        # Download multiple URLs
        sidekick knowledge download web "https://example.com/page1" "https://example.com/page2"
    """
    try:
        from ..knowledge.config import WebSourceConfig
        from ..knowledge.web import WebSource

        # Create temporary config
        config = WebSourceConfig(name="web-download", urls=urls, depth=depth)

        source = WebSource(config, output.parent)
        source.output_dir = output  # Override output directory

        console.print(f"[bold blue]Downloading {len(urls)} URL(s) to {output}...[/bold blue]")

        result = source.download(urls=urls, depth=depth)

        if result.success:
            console.print(f"[green]✓ Downloaded {len(result.files_downloaded)} files[/green]")
        else:
            console.print("[red]✗ Download failed[/red]")
            for error in result.errors:
                console.print(f"  [red]{error}[/red]")
            raise typer.Exit(1) from None

    except ImportError:
        console.print("[red]✗ Web source not implemented yet[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗ Download failed: {e}[/red]")
        raise typer.Exit(1) from None


@knowledge_app.command()
def reindex(
    knowledge_path: Path | None = typer.Option(
        None, "--knowledge-path", "-k", help="Path to knowledge documents directory"
    ),
    vector_db_path: Path | None = typer.Option(None, "--vector-db-path", "-v", help="Path for vector database storage"),
    table_name: str = typer.Option("rhdh_docs", "--table-name", "-t", help="Name of the LanceDB table"),
):
    """Reindex the knowledge base by recreating the LanceDB vector database.

    This command will reload all documents and rebuild the vector embeddings,
    which can be useful when documents have been updated or the vector database
    has become corrupted.

    Examples:
        # Reindex with default paths
        sidekick knowledge reindex

        # Reindex with custom paths
        sidekick knowledge reindex --knowledge-path ./docs --vector-db-path ./vectordb

        # Reindex with custom table name
        sidekick knowledge reindex --table-name my_docs
    """
    try:
        from ..knowledge import KnowledgeManager

        console.print("[blue]🔄 Starting knowledge base reindexing...[/blue]")

        # Create knowledge manager with specified paths
        manager = KnowledgeManager(
            knowledge_path=knowledge_path,
            vector_db_path=vector_db_path,
            table_name=table_name,
        )

        # Display current configuration
        console.print(f"[dim]Knowledge path: {manager.knowledge_path}[/dim]")
        console.print(f"[dim]Vector DB path: {manager.vector_db_path}[/dim]")
        console.print(f"[dim]Table name: {manager.table_name}[/dim]")

        if not manager.knowledge_path.exists():
            console.print(f"[red]✗ Knowledge path not found: {manager.knowledge_path}[/red]")
            raise typer.Exit(1) from None

        # Count documents for reference
        md_files = list(manager.knowledge_path.rglob("*.md"))
        pdf_files = list(manager.knowledge_path.rglob("*.pdf"))
        total_files = len(md_files) + len(pdf_files)

        if total_files == 0:
            console.print(f"[yellow]⚠ No documents found in {manager.knowledge_path}[/yellow]")
            raise typer.Exit(1) from None

        console.print(f"[dim]Found {len(md_files)} markdown and {len(pdf_files)} PDF files[/dim]")

        # Perform reindexing
        console.print("[blue]📚 Reindexing knowledge base (this may take a while)...[/blue]")
        manager.reindex_sync()

        console.print("[green]✓ Knowledge base reindexed successfully![/green]")
        console.print(f"[dim]Processed {total_files} documents[/dim]")

    except ImportError as e:
        console.print(f"[red]✗ Missing dependencies for knowledge management: {e}[/red]")
        console.print("[yellow]Install with: uv add agno[/yellow]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗ Reindexing failed: {e}[/red]")
        raise typer.Exit(1) from None
