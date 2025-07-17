#!/usr/bin/env python3
"""
Simple image analysis team test - similar to the shopping list example.
"""

import base64
import os
import uuid
from pathlib import Path

from agno.agent import Agent
from agno.media import Image
from agno.models.google import Gemini
from agno.team import Team
from dotenv import load_dotenv
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Load environment variables from .env file
load_dotenv()

# Set environment variables for Langfuse (with null checks)
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST")

if False:
    LANGFUSE_AUTH = base64.b64encode(f"{langfuse_public_key}:{langfuse_secret_key}".encode()).decode()
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = langfuse_host
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

    # Configure the tracer provider
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
    trace_api.set_tracer_provider(tracer_provider=tracer_provider)

    # Start instrumenting agno
    AgnoInstrumentor().instrument()
    print("🔍 Langfuse tracing enabled!")
else:
    print("⚠️  Langfuse environment variables not set - tracing disabled")

# Create image analysis agent
image_agent = Agent(
    name="Image Analyzer",
    role="Analyzes images and reports on image accessibility",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=[
        "You are an image analysis specialist.",
        "ALWAYS start your response by stating:",
        "1. Current time",
        "2. Whether you can see any images",
        "3. If you can see images, how many and describe them",
        "4. If you cannot see images, explicitly state 'No images available to me'",
        "Be detailed about what you can see in each image.",
    ],
)

# Create text analysis agent
text_agent = Agent(
    name="Text Analyzer",
    role="Analyzes text but also reports on image accessibility",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=[
        "You are a text analysis specialist.",
        "ALWAYS start your response by stating:",
        "1. Current time",
        "2. Whether you can see any images",
        "3. If you can see images, how many and describe them briefly",
        "4. If you cannot see images, explicitly state 'No images available to me'",
        "Then focus on text analysis.",
    ],
)

# Create the team with session state
image_team = Team(
    name="Image Analysis Team",
    mode="coordinate",
    model=Gemini(id="gemini-2.0-flash"),
    members=[image_agent, text_agent],
    team_session_state={"images_seen": [], "analysis_count": 0},
    session_state={"test_results": []},
    instructions=[
        "You coordinate image and text analysis.",
        "ALWAYS start your response by stating:",
        "1. Current time",
        "2. Whether you (team leader) can see any images",
        "3. How many images were provided to the team",
        "4. Update team_session_state with image analysis results",
        "Then delegate to your team members and synthesize their responses.",
    ],
    show_members_responses=True,
    markdown=True,
)

# Generate session ID
session_id = str(uuid.uuid4())
print(f"Using session ID: {session_id}")
print()

# Test 1: Load PNG files and test with images
print("=" * 60)
print("Test 1: With PNG images from tmp/")
print("=" * 60)

# Find PNG files in tmp directory
png_files = list(Path("tmp").glob("*.png"))
print(f"Found {len(png_files)} PNG files: {[f.name for f in png_files]}")


# Load images
images = []
for png_file in png_files[:1]:
    try:
        image = Image(filepath=str(png_file))
        images.append(image)
        print(f"Loaded: {png_file.name}")
    except Exception as e:
        print(f"Failed to load {png_file.name}: {e}")

# Run team with images
response1 = image_team.run(
    "Analyze these PNG images and report on image accessibility timing. Focus on when each agent can see the images.",
    images=images,
    session_id=session_id,
)
print(response1.content)
print(f"Team session state: {image_team.team_session_state}")
print(f"Session state: {image_team.session_state}")
print()

# Test 2: Follow-up question
print("=" * 60)
print("Test 2: Follow-up question")
print("=" * 60)
response2 = image_team.run("Summarize what you learned about image accessibility patterns.", session_id=session_id)
print(response2.content)
print(f"Team session state: {image_team.team_session_state}")
print(f"Session state: {image_team.session_state}")

print("\n✅ Image accessibility test completed!")
if langfuse_public_key and langfuse_secret_key and langfuse_host:
    print("🔍 Check your Langfuse dashboard for detailed traces!")
