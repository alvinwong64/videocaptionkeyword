from LLM_utils import encode_image, summarize_image, initialize_chat_gpt
import streamlit as st 
import os
import json
from video_utils import validate_youtube_link, download_video, video_file_to_frames, image_grid
from LLM_utils import summarize_image, encode_image, initialize_chat_gpt
from langchain_openai import ChatOpenAI

session = st.empty()
container = session.container()

# Landing page
def landing_page():

    st.title("Upload Video or Paste YouTube URL")
    # File upload section
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"],)
    youtube_url = st.text_input("Or paste a YouTube video URL here:")     

    if st.button("Generate Caption and Keywords"):
        if uploaded_file:
            st.session_state["video_file"] = uploaded_file
            st.session_state["source"] = "upload"
            st.session_state["page"] = "processing"  # Move to next page
            session.empty()
            st.rerun()
        elif youtube_url:
            valid, error = validate_youtube_link(youtube_url)
            if not valid:
                st.error(error)
                return
            st.session_state["video_url"] = youtube_url
            st.session_state["source"] = "youtube"
            st.session_state["page"] = "processing"  # Move to next page
            session.empty()
            st.rerun()
        else:
            st.popover("Please upload a video or provide a YouTube link.", icon="⚠️")


# Processing page (results)
def processing_page(chain_gpt):
    video_file = st.session_state.get("video_file")
    source = st.session_state.get("source")
    youtube_url = st.session_state.get("video_url")


    title_text = st.empty()
    title_text.title("Processing Video...")

    progress_text = st.empty()
    
    if not video_file and not youtube_url:
        st.error("No video selected. Please go back to the landing page.")
        st.button("Go Back",on_click=back_button)
    
    if source == "upload" and video_file:
        progress_text.text(f"Processing video from the uploaded file: {video_file.name}")
        filename = "input_vid.mp4"
        with open(filename, "wb") as f:
            f.write(video_file.getbuffer()) 
        
    elif source == "youtube" and youtube_url:
        progress_text.text(f"Processing video from YouTube URL .... {youtube_url}")
        filename = download_video(youtube_url)

    else:
        st.error("No video source detected. Please go back to the landing page.")
        st.button("Go Back",on_click=back_button)
    
    progress_text.text("Generating Caption and Keywords.....")

    frames = video_file_to_frames(filename)
    img_grid = image_grid(frames)
    img_grid.save("input_grid.jpg") 
    encoded_image = encode_image("input_grid.jpg")
    respond = summarize_image(encoded_image, chain_gpt)
    data = json.loads(respond)
    captions, keywords = data["caption"], data["keywords"]

    progress_text.empty()

    title_text.title("Your Caption and Keywords are ready!")
    st.markdown(f"**Caption**: {captions}")
    st.video(filename)
    st.markdown(f"**Keywords**:")
    st.markdown("""
        <style>
        .keyword-bubble {
            display: inline-block;
            background-color: #f0f0f0;
            color: #333;
            padding: 6px 12px;
            margin: 4px;
            border-radius: 12px;
            font-size: 14px;
            box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .keyword-container {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="keyword-container">' +
                ''.join([f'<span class="keyword-bubble">{word}</span>' for word in keywords]) +
                '</div>', unsafe_allow_html=True)
    st.markdown(r"")
    st.button("Go Back",on_click=back_button)


# Back button to return to the landing page
def back_button():
    session.empty()
    st.session_state["page"] = "landing"
    video_filename = "input_vid.mp4"
    grid_filename = "input_grid.jpg"    
    if os.path.exists(video_filename):
        os.remove(video_filename)
    if os.path.exists(grid_filename):
        os.remove(grid_filename)
    st.session_state.pop("video_file", None)
    st.session_state.pop("video_url", None)

def api_key_input():
    OPENAI_API_KEY = st.sidebar.text_input("OpenAI API Key", type="password")
    st.session_state["OPENAI_API_KEY"] = OPENAI_API_KEY
    if not st.session_state["OPENAI_API_KEY"].startswith("sk-"):
        st.warning("Please enter your OpenAI API key!", icon="⚠")
    else:
        try:    
            chain_gpt= ChatOpenAI(model="gpt-4o-mini", temperature= 0.8, max_tokens=4000, api_key=st.session_state["OPENAI_API_KEY"])
        except:
            st.warning("Incorrect API key!", icon="⚠")
    return chain_gpt

def main():
    try:
        chain_gpt = api_key_input()
    except:
        pass
    if "page" not in st.session_state:
        st.session_state["page"] = "landing"  # Set default page
    
    with container:
        if st.session_state["page"] == "landing":
            landing_page()
        elif st.session_state["page"] == "processing":
            processing_page(chain_gpt)

if __name__ == "__main__":
    main()
