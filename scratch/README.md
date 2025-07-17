# Image Analysis Team Test

This directory contains a test implementation to explore **image accessibility between agents** in an agno team structure.

## Files

- `image_analysis_team.py` - Main team implementation with two specialized agents
- `test_image_team.py` - Test script to demonstrate the team functionality
- `README.md` - This documentation file

## Team Structure

The `ImageAnalysisTeam` uses a **coordinate mode** with two specialized agents:

1. **Image Analyzer** - Specializes in analyzing visual content
2. **Text Analyzer** - Analyzes text content and also reports on image accessibility

## Key Test Questions

This implementation is designed to answer:

1. **When are images accessible?** - At what point in the team coordination flow do agents receive images?
2. **Which agents can see images?** - Do all agents in the team get access to images, or only specific ones?
3. **Timing of image upload** - When exactly are images made available to the agents?

## How to Test

### Basic Usage

```python
from scratch.image_analysis_team import ImageAnalysisTeam

# Create team
team = ImageAnalysisTeam(user_id="test_user")

# Test without image
response1 = team.analyze_with_image("Analyze this text.")

# Test with image
response2 = team.analyze_with_image("Analyze this content.", "/path/to/image.jpg")

# Follow-up question
response3 = team.ask("What did you learn about image accessibility?")
```

### Run the Test Script

```bash
cd scratch
python test_image_team.py
```

## Expected Behavior

Each agent is instructed to report:

1. **Current time** when they process the request
2. **Whether they can see any images**
3. **If they can see images, describe what they see**
4. **Their primary analysis** (text or image analysis)

## Key Features

- **Timestamp tracking** - All agents report current time to track when images become available
- **Explicit image reporting** - Each agent must state whether they can see images
- **Session management** - Uses persistent sessions to track conversation flow
- **Detailed logging** - Comprehensive logging for debugging image accessibility

## Testing Image Accessibility

The implementation includes specific instructions for each agent to:

- Always start responses by stating current time and image visibility
- Explicitly report if no images are available
- Describe images in detail when they can see them
- Focus on the timing and accessibility patterns

This allows us to understand exactly when and how images flow through the team coordination system.
