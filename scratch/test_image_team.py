#!/usr/bin/env python3
"""
Test script for the Image Analysis Team.

This script demonstrates how to use the ImageAnalysisTeam to test
image accessibility between agents.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scratch.image_analysis_team import ImageAnalysisTeam


def main():
    """Main test function."""
    print("🔍 Testing Image Analysis Team - Image Accessibility Test\n")

    # Create team instance
    team = ImageAnalysisTeam(work_dir=Path("tmp/image_test_work"), user_id="test_user")

    # Test 1: Analysis without image
    print("=" * 60)
    print("Test 1: Analysis without image")
    print("=" * 60)

    try:
        response1 = team.analyze_with_image(
            "Hello, this is a test message without an image. Please analyze this text and "
            "report on image accessibility."
        )
        print("✅ Team Response:")
        print(response1.content)
        print("\n")
    except Exception as e:
        print(f"❌ Error in Test 1: {e}")
        print("\n")

    # Test 2: Analysis with PNG files from tmp directory
    print("=" * 60)
    print("Test 2: Analysis with PNG files from tmp directory")
    print("=" * 60)

    try:
        response2 = team.analyze_with_png_files(
            "Please analyze the PNG images found in the tmp directory. Focus on reporting "
            "image accessibility timing and which agents can see which images."
        )
        print("✅ Team Response:")
        print(response2.content)
        print("\n")
    except Exception as e:
        print(f"❌ Error in Test 2: {e}")
        print("\n")

    # Test 3: Follow-up question in the same session
    print("=" * 60)
    print("Test 3: Follow-up question")
    print("=" * 60)

    try:
        response3 = team.ask(
            "Based on our previous interactions, can you summarize what you learned about image accessibility timing?"
        )
        print("✅ Team Response:")
        print(response3.content)
        print("\n")
    except Exception as e:
        print(f"❌ Error in Test 3: {e}")
        print("\n")

    print("🎉 Test completed!")


if __name__ == "__main__":
    main()
