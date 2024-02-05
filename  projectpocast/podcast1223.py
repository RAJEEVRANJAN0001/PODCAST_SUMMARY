# Save this code into a file named 'podcast_summary.py'

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


# Streamlit UI code
st.title('Welcome to my application that creates Podcast summaries')
episode_id = st.text_input('Please input the episode id from listen-notes')
button = st.button('Get podcast summary!')

def get_clean_time(start_ms):
    seconds = int((start_ms / 1000) % 60)
    minutes = int((start_ms / (1000 * 60)) % 60)
    hours = int((start_ms / (1000 * 60 * 60)) % 24)
    if hours > 0:
        start_t = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    else:
        start_t = f'{minutes:02d}:{seconds:02d}'
        
    return start_t

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
        with st.expander(chp['gist'] + '_' + get_clean_time(chp['start'])):
            st.write(chp['summary'])
