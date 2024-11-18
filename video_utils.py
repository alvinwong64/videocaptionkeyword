from pytubefix import YouTube
import cv2
from PIL import Image
import re


def download_video(url):
    """
    Download a video from a given url and save it to the output path.
    """
    
    yt = YouTube(url)
    filename ="input_vid"
    yt.streams.get_highest_resolution().download(
        filename=filename
    )
    return filename +".mp4"

def video_file_to_frames(video_file_path):
    """
    Extract 9 evenly spaced frames from a video file.

    Args:
        video_file_path (str): Path to the video file.

    Returns:
        list: A list of extracted frames as PIL Image objects.
    """
    cap = cv2.VideoCapture(video_file_path)

    if not cap.isOpened():
        raise ValueError("Could not open the video file.")

    # Get total frames and calculate the interval
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(1, total_frames // 9)

    frame_indices = [i * interval for i in range(9)]
    extracted_frames = []

    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)  # Jump to the frame
        ret, frame = cap.read()
        if not ret:
            print(f"Frame {frame_index} could not be read, skipping...")
            continue
        # Convert the frame from BGR to RGB and then to a PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        extracted_frames.append(pil_image)

    cap.release()
    return extracted_frames


def image_grid(frames, grid_shape=(3, 3), padding=10):
    """
    Combine frames into a grid, filling missing frames with white placeholders.

    Args:
        frames (list): List of frames as PIL Image objects.
        grid_shape (tuple): The grid shape (rows, columns), default is (3, 3).
        padding (int): Padding between images in pixels.

    Returns:
        PIL.Image.Image: The combined image in a grid layout.
    """
    rows, cols = grid_shape
    total_cells = rows * cols

    # Get the size of each frame
    if frames:
        frame_width, frame_height = frames[0].size
    else:
        raise ValueError("No frames provided to create the grid.")

    # Calculate the size of the grid image
    grid_width = frame_width * cols + padding * (cols - 1)
    grid_height = frame_height * rows + padding * (rows - 1)
    grid_image = Image.new("RGB", (grid_width, grid_height), color=(255, 255, 255))

    # Paste each frame into the grid
    for idx in range(total_cells):
        row = idx // cols
        col = idx % cols

        x_start = col * (frame_width + padding)
        y_start = row * (frame_height + padding)

        if idx < len(frames):
            grid_image.paste(frames[idx], (x_start, y_start))
    # grid_image = grid_image.resize((512, 512))

    return grid_image

def validate_youtube_link(url, max_duration=300):
    """
    Validate a YouTube link with multiple checks.
    
    Args:
        url (str): The YouTube URL to validate.
        max_duration (int): Maximum allowed duration for the video in seconds.
    
    Returns:
        list: [bool, str or None]. True if valid, otherwise False and an error reason.
    """
    # Check for valid YouTube URL structure
    youtube_regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$"
    if not re.match(youtube_regex, url):
        return [False, "Invalid URL format. Please enter a valid YouTube link."]
    
    # Check if it is a playlist
    if "playlist" in url:
        return [False, "The provided link is a playlist. Please enter a single video URL."]
    
    # Try to load the YouTube video
    try:
        yt = YouTube(url)
    except Exception as e:
        return [False, f"Error loading the video: {e}"]
    
    # Check video duration
    if yt.length > max_duration:
        return [False, f"The video exceeds the {max_duration}-second length limit."]

    # If all checks pass
    return [True, None]

