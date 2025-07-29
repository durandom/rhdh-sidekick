#!/usr/bin/env python3
"""
Example usage of the Google Drive toolkit.

This example demonstrates how to use the GoogleDriveTools toolkit to download
documents from Google Drive to a local workspace directory.
"""

from pathlib import Path

from agno.agent import Agent

from sidekick.tools import GoogleDriveTools


def main():
    """Main example function."""
    # Initialize the Google Drive toolkit
    # The toolkit will use ./workspace as the default download directory
    gdrive_tools = GoogleDriveTools(
        workspace_dir=Path("./workspace"),
        credentials_path=Path(".client_secret.googleusercontent.com.json"),
    )

    # Create an agent with the Google Drive tools
    agent = Agent(
        tools=[gdrive_tools],
        show_tool_calls=True,
        markdown=True,
    )

    print("Google Drive Toolkit Example")
    print("=" * 40)

    # Example 1: List supported formats
    print("\n1. Checking supported formats for documents:")
    response = agent.run("What export formats are supported for Google Documents?")
    print(response.content)

    # Example 2: Download a single document
    print("\n2. Example download command:")
    print("To download a Google Doc as HTML:")
    print('agent.run("Download this Google Doc as HTML: https://docs.google.com/document/d/YOUR_DOC_ID/edit")')

    # Example 3: Get user info
    print("\n3. Getting authenticated user info:")
    response = agent.run("Who is the currently authenticated Google Drive user?")
    print(response.content)

    print("\n" + "=" * 40)
    print("To use this toolkit with real documents:")
    print("1. Set up Google Drive API credentials")
    print("2. Place the credentials file as .client_secret.googleusercontent.com.json")
    print("3. Run authentication flow on first use")
    print("4. Use agent.run() with natural language commands like:")
    print('   - "Download this document as PDF: <google-drive-url>"')
    print('   - "Download these 3 documents as markdown: <url1>, <url2>, <url3>"')
    print('   - "What formats can I export a spreadsheet to?"')


if __name__ == "__main__":
    main()
