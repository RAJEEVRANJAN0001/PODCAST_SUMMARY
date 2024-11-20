# Podcast Summary Application

podcast_summary.py is a Python-based application that retrieves podcast episodes, transcribes audio content using AssemblyAI, and creates summaries with chapter breakdowns. The application also includes a user-friendly interface built with Streamlit for interaction.

# Features
Audio Retrieval: Fetches audio URLs and metadata from ListenNotes API.
Transcription Service: Transcribes podcast audio using AssemblyAI with support for automatic chapter creation.
Streamlit UI: Interactive UI with a modern dark theme for ease of use.
Custom CSS Styling: Styled components for a visually appealing experience.

# Usage Instructions
Start the app and enter the podcast episode ID from ListenNotes.
Click Get podcast summary! to generate the summary.
View the structured podcast summary with chapters and their details.
Saved files include:
<episode_id>.txt: Complete transcript.
<episode_id>_chapters.json: JSON with chapter details.

# Requirements
Python 3.7 or higher
Required libraries:
requests
json
time
pprint
streamlit

# Developer
This application was developed by Rajeev Ranjan Pratap Singh.
For suggestions or contributions, feel free to create issues or submit pull requests!
