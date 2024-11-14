import os
import praw
from openai import OpenAI
from moviepy.editor import VideoFileClip, clips_array
import moviepy.editor as mp
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()


def get_popular_reddit_post():
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )
    subreddit = reddit.subreddit("AmItheAsshole")
    popular_post = subreddit.top(time_filter="week", limit=1).__next__()
    return popular_post.title, popular_post.selftext


def generate_audio(transcript):
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # audio = openai.Audio.create(
    #     prompt=transcript, model="whisper-small", response_format="mp3"
    # )
    # with open("output_audio.mp3", "wb") as f:
    #     f.write(audio.audio_binary)

    client = OpenAI(api_key=openai_api_key)

    # TODO 2024-11-14: @pchoi stopped here after my internet died 🥲🥲🥲

    response = client.audio.speech.create(
        model="whisper-small",
        # voice="nova",
        input=transcript,
    )

    response.stream_to_file("output.mp3")


def create_video(source_image, video_clip, audio_duration):
    src_image = Image.open(source_image)
    video = VideoFileClip(video_clip)

    video = video.subclip(0, audio_duration)

    image_width, image_height = src_image.size
    if image_width / image_height > 16 / 9:
        new_width = int(image_height * 16 / 9)
        new_height = image_height
    else:
        new_width = image_width
        new_height = int(image_width * 9 / 16)
    src_image = src_image.resize((new_width, new_height))
    src_image = src_image.crop(((new_width - 640) // 2, 0, (new_width + 640) // 2, 360))

    final_clip = clips_array([[src_image], [video]])
    final_clip.write_videofile("output_video.mp4")


def create_graphic(title, text):
    # Create a 16:9 image
    image_width, image_height = 1280, 720
    image = Image.new("RGB", (image_width, image_height), (255, 255, 255))

    # Draw the title and text on the image
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", size=36)

    # Draw the title
    draw.text((50, 50), title, font=font, fill=(0, 0, 0))

    # Draw the text
    x, y = 50, 150
    for line in text.split("\n"):
        draw.text((x, y), line, font=font, fill=(0, 0, 0))
        y += 50

    image.save("source_image.png")


if __name__ == "__main__":
    title, text = get_popular_reddit_post()
    generate_audio(text)
    create_graphic(title, text)

    audio = mp.AudioFileClip("output_audio.mp3")
    audio_duration = audio.duration

    create_video("source_image.png", "/input_clips/surfers.mp4", audio_duration)
    print(f"Video generated: output_video.mp4")
