#!/usr/bin/env python3
"""
Test the updated sidekick GCS implementation.
"""

import os
import sys

# Add sidekick to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sidekick.tools.test_analysis import get_test_analysis_prompt, storage_client


def test_sidekick_gcs():
    """Test the sidekick GCS implementation."""
    print("Testing sidekick GCS implementation...")

    # Test data
    base_dir = "logs/periodic-ci-redhat-developer-rhdh-main-e2e-tests-gke-operator-nightly/1945046040382017536"
    artifacts_dir = f"{base_dir}/artifacts/"

    try:
        print(f"Testing get_immediate_directories for: {artifacts_dir}")
        directories = storage_client.get_immediate_directories(artifacts_dir)
        print(f"Found directories: {directories}")

        e2e_dirs = [d for d in directories if d.startswith("e2e-tests-")]
        print(f"E2E test directories: {e2e_dirs}")

        if e2e_dirs:
            print("✅ Successfully found e2e test directories!")

            # Now test the full prompt generation
            print("\nTesting get_test_analysis_prompt...")
            prompt = get_test_analysis_prompt(base_dir)
            print(f"Generated prompt (first 500 chars): {prompt[:500]}...")

            if prompt and len(prompt) > 100:
                print("✅ Successfully generated test analysis prompt!")
                return True
            else:
                print(f"❌ Prompt too short or empty: {len(prompt)} characters")
                return False
        else:
            print("❌ No e2e test directories found")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_sidekick_gcs()
    if success:
        print("\n✅ All tests passed! Sidekick GCS implementation is working.")
    else:
        print("\n❌ Tests failed. Need to debug further.")
