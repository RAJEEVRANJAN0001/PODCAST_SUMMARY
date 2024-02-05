# podcast_summary.py

import requests
import json
import time
import pprint
import streamlit as st

transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'
assemblyai_headers = {'authorization': 'a10699bee56b4f51b2a3e7abdd5bba3e'}

listennotes_episode_endpoint = "https://listen-api.listennotes.com/api/v2/episodes"
listennotes_headers = {'X-ListenAPI-Key': '7fc45ec5e69546519f24af66cc4a4b1b'}

def get_episode_audio_url(episode_id):
    url = listennotes_episode_endpoint + '/' + episode_id
    response = requests.request('GET', url, headers=listennotes_headers)

    try:
        response.raise_for_status()
        data = response.json()

        if 'title' in data:
            episode_title = data['title']
        else:
            episode_title = "Unknown Episode Title"

        thumbnail = data.get('thumbnail', "Unknown Thumbnail")
        podcast_title = data.get('podcast', {}).get('title', "Unknown Podcast Title")
        audio_url = data.get('audio', "Unknown Audio URL")

        return audio_url, thumbnail, podcast_title, episode_title

    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Error:", err)

    return None, None, None, None

def transcribe(audio_url, auto_chapters):
    transcript_request = {
        'audio_url': audio_url,
        'auto_chapters': auto_chapters
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=assemblyai_headers)
    pprint.pprint(transcript_response.json())
    return transcript_response.json()['id']

def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=assemblyai_headers)
    return polling_response.json()

def get_transcription_result_url(url, auto_chapters):
    transcribe_id = transcribe(url, auto_chapters)
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']

        print("waiting for 60 seconds")
        time.sleep(60)

def save_transcript(episode_id):
    audio_url, thumbnail, podcast_title, episode_title = get_episode_audio_url(episode_id)
    if audio_url is None:
        print("Error retrieving episode information.")
        return False

    data, error = get_transcription_result_url(audio_url, auto_chapters=True)

    pprint.pprint(data)

    if data:
        filename = episode_id + '.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])

        chapters_filename = episode_id + '_chapters.json'
        with open(chapters_filename, 'w') as f:
            chapters = data['chapters']

            episode_data = {'chapters': chapters}
            episode_data['episode_thumbnail'] = thumbnail
            episode_data['podcast_title'] = podcast_title
            episode_data['episode_title'] = episode_title

            json.dump(episode_data, f)
            print('Transcript saved')
            return True
    elif error:
        print("Error!!!", error)
        return False

# Streamlit UI code with added CSS styling
st.title('Welcome to my application that creates Podcast summaries')

# Add custom CSS styling with dark grey background
st.markdown(
    """
    <style>
        body {
            background-color: #333333; /* Dark grey background color */
            color: #ffffff; /* White text color */
            font-family: 'Arial', sans-serif;
        }
        .stImage {
            max-width: 300px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .stButton {
            background-color: #3498db;
            color: #ffffff;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            display: inline-block;
        }
        .stButton:hover {
            background-color: #297fb8;
        }
        .stExpander {
            border: 1px solid #dddddd;
            border-radius: 8px;
            margin: 10px 0;
        }
        .bottom-right {
            position: fixed;
            right: 10px;
            bottom: 10px;
            max-width: 200px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Add the image at the top left side
image_path_top = 'im1-removebg-preview.png'  # Replace with the actual path to your image
st.image(image_path_top)

episode_id = st.text_input('Please input the episode id from listen-notes')
# Use st.markdown to create a styled button
button = st.button('Get podcast summary!')
if button:
    filename = episode_id + '_chapters.json'
    with open(filename, 'r') as f:
        data = json.load(f)

    chapters = data['chapters']
    podcast_title = data['podcast_title']
    episode_title = data['episode_title']
    thumbnail = data['episode_thumbnail']

    st.header(f'{podcast_title} - {episode_title}')
    st.image(thumbnail)
    for chp in chapters:
        st.markdown(
            f"""
            <details class="stExpander">
                <summary>{chp['gist']}_{get_clean_time(chp['start'])}</summary>
                <p>{chp['summary']}</p>
            </details>
            """,
            unsafe_allow_html=True
        )

# Add the image at the bottom right corner
image_path_bottom = 'Untitled design.jpg'  # R
st.image(image_path_bottom, width=100)  # Adjust the width as needed

# Add developer message
st.write("This was developed by Rajeev Ranjan Pratap Singh")
