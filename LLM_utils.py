import base64
from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def encode_image(image_path):
    """
    Encode an image to base64 format.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

    
def summarize_image(encoded_image, chain_gpt):
    """
    Summarize an image using a given chain of GPT model.
    The image grid is not resized, as it is now for prototyping purpose only. 
    Resizing image also will loss information and slightly affects the caption and keyword generation.
    """
    prompt = [
        AIMessage(
            content=""" You are a professional stock photo caption and keyword generator that is highly skilled in analyzing images and generating detailed captions and relevant keywords for a stock photo website. 
                        Given a grid of 9 frames extracted from a video, your task is to:
                        1. Provide a ** caption** or **title** within 20 words that accurately summarizes the key content and visual theme of the video, based on the images in the grid. The caption should be relevant and professional, suitable for a stock photo website.
                        2. Generate a list of **keywords** that describe the main themes, objects, actions, people, and environments depicted in the frames. The keywords should be specific, relevant, and optimized for searchability on a stock photo platform. Generate not less than 20 keywords, up to 50 keywords.

                        For reference, stock photo websites often focus on:
                        - Describing the mood, color palette, and visual tone of the content
                        - Identifying specific objects, actions, or scenes in the images (e.g., "business meeting", "nature", "portrait", etc.)
                        - Including descriptive terms that align with what potential customers might search for.
                        Please ensure that the keywords cover various aspects of the video content and are phrased in a way that would maximize discoverability on a stock photo site."""
                  ),

        HumanMessage(content=[
            {"type": "text", "text": "Provide the caption and keywords for the following image that is extracted from a video."},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                },
            },
        ]),
        AIMessage(content="Provide the output in the format of string of a dictionary with two keys: caption and keywords, where caption is a string and keywords is a list of strings. Do not give json format"),
    ]

    response = chain_gpt.invoke(prompt)
    return response.content

def initialize_chat_gpt():
    """
    Initialize a chat GPT model with the given parameters.
    """
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(model="gpt-4o-mini", temperature= 0.8, max_tokens=4000, api_key=OPENAI_API_KEY)
