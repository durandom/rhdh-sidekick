#!/usr/bin/env python3
"""
Test script to debug JUnit XML parsing error.
"""

import os
import sys
import xml.etree.ElementTree as ET

# Add sidekick to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sidekick.tools.test_analysis import storage_client


def test_junit_xml_parsing():
    """Test parsing the problematic JUnit XML file."""
    xml_path = (
        "logs/periodic-ci-redhat-developer-rhdh-main-e2e-tests-gke-operator-nightly/"
        "1945046040382017536/artifacts/e2e-tests-gke-operator-nightly/"
        "redhat-developer-rhdh-gke-operator-nightly/artifacts/showcase-k8s-ci-nightly/junit-results.xml"
    )

    try:
        print(f"Testing JUnit XML file: {xml_path}")

        # First, let's check if the file exists
        exists = storage_client.blob_exists(xml_path)
        print(f"File exists: {exists}")

        if not exists:
            print("❌ File does not exist")
            return False

        # Get the raw content
        print("\nRetrieving raw content...")
        raw_content = storage_client.get_text_from_blob(xml_path)
        print(f"Raw content length: {len(raw_content)} characters")
        print(f"First 200 characters: {repr(raw_content[:200])}")
        print(f"Last 200 characters: {repr(raw_content[-200:])}")

        # Check if it's empty
        if not raw_content.strip():
            print("❌ File is empty")
            return False

        # Try to parse as XML
        print("\nTrying to parse as XML...")
        try:
            root = ET.fromstring(raw_content)
            print(f"✅ Successfully parsed XML. Root tag: {root.tag}")

            # Check attributes
            print(f"Root attributes: {root.attrib}")

            # Look for testsuites
            if root.tag == "testsuite":
                testsuites = [root]
                print("Single testsuite found")
            else:
                testsuites = root.findall("testsuite")
                print(f"Found {len(testsuites)} testsuites")

            # Check for failures
            for i, testsuite in enumerate(testsuites):
                failures = int(testsuite.get("failures", "0"))
                errors = int(testsuite.get("errors", "0"))
                tests = int(testsuite.get("tests", "0"))
                name = testsuite.get("name", "Unknown")

                print(f"Testsuite {i + 1}: {name}")
                print(f"  Tests: {tests}, Failures: {failures}, Errors: {errors}")

                if failures > 0 or errors > 0:
                    print(f"  ⚠️  Found {failures} failures and {errors} errors")

                    # Look for failure elements
                    failure_elements = testsuite.findall(".//failure")
                    error_elements = testsuite.findall(".//error")

                    print(f"  Failure elements: {len(failure_elements)}")
                    print(f"  Error elements: {len(error_elements)}")

                    for j, failure in enumerate(failure_elements[:2]):  # Show first 2 failures
                        print(f"    Failure {j + 1}: {failure.get('message', 'No message')[:100]}...")

            return True

        except ET.ParseError as e:
            print(f"❌ XML Parse Error: {e}")

            # Try to find the problematic area
            lines = raw_content.split("\n")
            print(f"Total lines: {len(lines)}")

            # Show first few lines
            print("\nFirst 10 lines:")
            for i, line in enumerate(lines[:10], 1):
                print(f"{i:2d}: {repr(line)}")

            # If it's a syntax error at line 1, column 0, it might be a binary file or have BOM
            if raw_content.startswith("\ufeff"):
                print("❌ File has BOM (Byte Order Mark)")
            elif raw_content.startswith(b"\x00".decode("utf-8", errors="ignore")):
                print("❌ File appears to be binary")
            elif not raw_content.startswith("<"):
                print("❌ File doesn't start with '<' - not XML")

            return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_working_xml():
    """Test with a working XML file for comparison."""
    xml_path = (
        "logs/periodic-ci-redhat-developer-rhdh-main-e2e-tests-gke-operator-nightly/"
        "1945046040382017536/artifacts/e2e-tests-gke-operator-nightly/"
        "redhat-developer-rhdh-gke-operator-nightly/artifacts/showcase-rbac-k8s-ci-nightly/junit-results.xml"
    )

    try:
        print(f"\n{'=' * 80}")
        print(f"Testing working XML file: {xml_path}")

        exists = storage_client.blob_exists(xml_path)
        print(f"File exists: {exists}")

        if not exists:
            print("❌ File does not exist")
            return False

        raw_content = storage_client.get_text_from_blob(xml_path)
        print(f"Raw content length: {len(raw_content)} characters")
        print(f"First 200 characters: {repr(raw_content[:200])}")

        # Parse XML
        root = ET.fromstring(raw_content)
        print(f"✅ Successfully parsed XML. Root tag: {root.tag}")

        return True

    except Exception as e:
        print(f"❌ Error with working XML: {e}")
        return False


if __name__ == "__main__":
    print("Testing JUnit XML parsing...")

    # Test the problematic file
    problematic_works = test_junit_xml_parsing()

    # Test a working file for comparison
    working_works = test_working_xml()

    print(f"\n{'=' * 80}")
    print("Results:")
    print(f"Problematic XML: {'✅ Works' if problematic_works else '❌ Failed'}")
    print(f"Working XML: {'✅ Works' if working_works else '❌ Failed'}")
