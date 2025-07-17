#!/usr/bin/env python3
"""
Simple test script to test PNG image accessibility in the Image Analysis Team.

This script focuses specifically on testing the PNG files found in the tmp directory
and tracks image accessibility timing between agents.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scratch.image_analysis_team import ImageAnalysisTeam


def main():
    """Test PNG image accessibility."""
    print("🖼️  Testing PNG Image Accessibility in Agent Team\n")

    # Create team instance
    team = ImageAnalysisTeam(work_dir=Path("tmp/image_test_work"), user_id="png_test_user")

    # Test: Analysis with PNG files from tmp directory
    print("=" * 80)
    print("Testing PNG Image Accessibility Across Agents")
    print("=" * 80)

    try:
        response = team.analyze_with_png_files(
            text="This is a test to understand when and how PNG images become accessible to "
            "different agents in the team. Please analyze the images and report exactly when "
            "each agent can see them.",
            png_dir="tmp",
        )
        print("✅ Team Response:")
        print(response.content)
        print("\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n")

    # Follow-up question about image accessibility
    print("=" * 80)
    print("Follow-up: Image Accessibility Summary")
    print("=" * 80)

    try:
        response2 = team.ask(
            "Based on your analysis, can you create a summary of image accessibility patterns? "
            "Specifically: 1) When did you first see the images? 2) Which agents could see the "
            "images? 3) Were all agents able to see all images at the same time?"
        )
        print("✅ Team Response:")
        print(response2.content)
        print("\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n")

    print("🎉 PNG Image Accessibility Test completed!")


if __name__ == "__main__":
    main()
