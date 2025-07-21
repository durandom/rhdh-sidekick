"""Google Drive export commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..utils.gdrive import GoogleDriveExporter, GoogleDriveExporterConfig

console = Console()

# Create the gdrive sub-application
gdrive_app = typer.Typer(
    name="gdrive",
    help="Google Drive document export commands",
    rich_markup_mode="rich",
)


@gdrive_app.command()
def export(
    document_ids: list[str] | None = typer.Argument(
        None, help="Google Drive document IDs or URLs to export (not used with --mirror)"
    ),
    format: str = typer.Option(
        "html", "--format", "-f", help="Export format: pdf, docx, odt, rtf, txt, html, epub, zip, or 'all'"
    ),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Output directory for exported files"),
    credentials: Path | None = typer.Option(
        None, "--credentials", "-c", help="Path to Google OAuth credentials JSON file"
    ),
    follow_links: bool = typer.Option(False, "--follow-links", "-l", help="Follow and export linked documents"),
    link_depth: int = typer.Option(0, "--depth", "-d", help="Maximum depth for following links (0-5)"),
    mirror: bool = typer.Option(
        False, "--mirror", "-m", help="Mirror documents from knowledge/rhdh/gdrive.txt to knowledge/rhdh/gdrive/"
    ),
    config_file: Path | None = typer.Option(
        None, "--config", help="Path to configuration file (default: knowledge/rhdh/gdrive.txt when using --mirror)"
    ),
):
    """Export Google Drive documents in various formats.

    Examples:
        # Export a single document as HTML
        sidekick gdrive export 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

        # Export from URL as PDF
        sidekick gdrive export "https://docs.google.com/document/d/DOCUMENT_ID/edit" -f pdf

        # Export multiple documents in all formats
        sidekick gdrive export doc_id_1 doc_id_2 -f all

        # Export with linked documents (2 levels deep)
        sidekick gdrive export doc_id --follow-links --depth 2

        # Mirror documents from configuration file
        sidekick gdrive export --mirror

        # Mirror with custom configuration file
        sidekick gdrive export --mirror --config my-docs.txt
    """
    # Validate arguments
    if mirror and document_ids:
        console.print("[bold red]✗ Cannot use document IDs with --mirror flag[/bold red]")
        raise typer.Exit(1)

    if not mirror and not document_ids:
        console.print("[bold red]✗ Must provide document IDs or use --mirror flag[/bold red]")
        raise typer.Exit(1)

    # Set default paths for mirror mode
    if mirror:
        if not output_dir:
            output_dir = Path("knowledge/rhdh/gdrive")
        if not config_file:
            config_file = Path("knowledge/rhdh/gdrive.txt")
    else:
        if not output_dir:
            output_dir = Path("exports")

    # Validate format
    valid_formats = {"pdf", "docx", "odt", "rtf", "txt", "html", "epub", "zip", "all"}
    if format not in valid_formats:
        console.print(f"[red]✗ Invalid format: {format}[/red]")
        console.print(f"Valid formats: {', '.join(sorted(valid_formats))}")
        raise typer.Exit(1) from None

    # Configure exporter
    config = GoogleDriveExporterConfig(
        target_directory=output_dir,
        export_format=format,  # type: ignore[arg-type]
        follow_links=follow_links,
        link_depth=link_depth,
    )

    if credentials:
        config.credentials_path = credentials

    # Create exporter
    exporter = GoogleDriveExporter(config)

    # Execute export or mirror
    if mirror:
        console.print(f"[bold blue]Mirroring documents from {config_file}...[/bold blue]")
        try:
            results = exporter.mirror_documents(config_file or Path("knowledge/rhdh/gdrive.txt"))
        except FileNotFoundError:
            console.print(f"[bold red]✗ Configuration file not found: {config_file}[/bold red]")
            console.print("[dim]Create the file with format:[/dim]")
            console.print("[dim]# RHDH Documentation Mirror[/dim]")
            console.print("[dim]# Format: URL [depth=N] [# comment][/dim]")
            console.print("[dim]https://docs.google.com/document/d/ID/edit depth=2 # Example doc[/dim]")
            raise typer.Exit(1) from None
        except Exception as e:
            console.print(f"[bold red]✗ Mirror failed: {e}[/bold red]")
            raise typer.Exit(1) from e
    else:
        if not document_ids:
            console.print("[red]✗ No document IDs provided[/red]")
            raise typer.Exit(1) from None
        console.print(f"[bold blue]Exporting {len(document_ids)} document(s)...[/bold blue]")
        results = exporter.export_multiple(document_ids)

    # Display results
    if results:
        table = Table(title="Export Results")
        table.add_column("Document ID", style="cyan")
        table.add_column("Formats", style="green")
        table.add_column("Files", style="yellow")

        for doc_id, exported_files in results.items():
            formats = ", ".join(exported_files.keys())
            # Show the filenames since they're all in the same directory now
            if exported_files:
                filenames = ", ".join([path.name for path in exported_files.values()])
                table.add_row(doc_id, formats, filenames)

        console.print(table)

        # Show summary
        if mirror:
            console.print(
                f"\n[bold green]✓ Mirror completed: {len(results)} document(s) exported to {output_dir}[/bold green]"
            )
        else:
            console.print(f"\n[bold green]✓ Successfully exported {len(results)} document(s)[/bold green]")
    else:
        console.print("[bold red]✗ No documents were exported[/bold red]")
        raise typer.Exit(1)


@gdrive_app.command()
def formats():
    """List available export formats."""
    table = Table(title="Available Export Formats")
    table.add_column("Format", style="cyan")
    table.add_column("Extension", style="green")
    table.add_column("Description", style="yellow")

    for key, format_info in GoogleDriveExporter.EXPORT_FORMATS.items():
        table.add_row(key, format_info.extension, format_info.description or "")

    console.print(table)
    console.print("\n[dim]Use --format=all to export in all formats[/dim]")


@gdrive_app.command()
def debug(
    document_id: str = typer.Argument(..., help="Google Drive document ID to debug"),
    credentials: Path | None = typer.Option(
        None, "--credentials", "-c", help="Path to Google OAuth credentials JSON file"
    ),
):
    """Debug access to a specific Google Drive document."""
    from ..utils.gdrive import GoogleDriveExporter, GoogleDriveExporterConfig

    # Configure exporter
    config = GoogleDriveExporterConfig()
    if credentials:
        config.credentials_path = credentials

    exporter = GoogleDriveExporter(config)

    # Show authenticated user info
    console.print("[bold blue]Authentication Info:[/bold blue]")
    user_info = exporter.get_authenticated_user_info()
    if user_info:
        console.print(f"Authenticated as: [green]{user_info.get('emailAddress', 'Unknown')}[/green]")
        console.print(f"Display name: [green]{user_info.get('displayName', 'Unknown')}[/green]")
    else:
        console.print("[red]Could not get user info[/red]")

    console.print(f"\n[bold blue]Testing access to document:[/bold blue] {document_id}")
    console.print(f"Document URL: https://docs.google.com/document/d/{document_id}/edit")

    try:
        # Test document access
        metadata = exporter.get_document_metadata(document_id)
        console.print("[green]✓ Document accessible![/green]")
        console.print(f"Title: {metadata.get('name', 'Unknown')}")
        console.print(f"MIME type: {metadata.get('mimeType', 'Unknown')}")
        console.print(f"Modified: {metadata.get('modifiedTime', 'Unknown')}")

        # Show owners if available
        owners = metadata.get("owners", [])
        if owners:
            console.print("Owners:")
            for owner in owners:
                console.print(f"  - {owner.get('displayName', 'Unknown')} ({owner.get('emailAddress', 'Unknown')})")

    except Exception as e:
        console.print(f"[red]✗ Cannot access document: {e}[/red]")
        console.print("\n[bold yellow]Troubleshooting steps:[/bold yellow]")
        console.print("1. Make sure the document is shared with your OAuth account")
        console.print("2. Check if you're using the correct Google account")
        console.print("3. Try setting document permissions to 'Anyone with the link can view'")
        raise typer.Exit(1) from e
