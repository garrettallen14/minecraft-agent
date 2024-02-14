import pygetwindow as gw
import pyautogui
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
import base64
import os

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))



def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def take_screenshot(name):
    # Find the window by title
    window_title = 'Minecraft 1.20.2 - Multiplayer (LAN)'
    titles = gw.getAllTitles()
    for title in titles:
        if 'Minecraft' in title:
            window_title = title
            break
    window = gw.getWindowsWithTitle(window_title)[0]  # Adjust index if necessary
    if window:
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        screenshot.save(name)

def visionModule(query, prompt='SYSTEM: You are answering questions for a Minecraft player. Based on the image provided, this is what the player wants to know:'):
    # Take screenshot
    take_screenshot('screenshot.png')
    base64_image = encode_image('screenshot.png')


    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{prompt} {query}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=690,  # default max tokens is low so set higher
    )

    # Accessing the generated output correctly
    return response.choices[0].message.content
