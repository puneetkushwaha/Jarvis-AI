import asyncio
import os
import requests
from random import randint
from PIL import Image
from dotenv import load_dotenv
from time import sleep

load_dotenv()
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_KEY = os.getenv("HuggingFaceAPIKey")

headers = {"Authorization": f"Bearer {API_KEY}"}

def check_and_create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_file_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except:
        return None

def update_file_status(file_path, status):
    try:
        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(status)
    except:
        pass

async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            return None
        return response.content
    except:
        return None

async def generate_image(prompt: str):
    check_and_create_folder("Data")
    tasks = []
    for _ in range(4):
        payload = {"inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"}
        tasks.append(asyncio.create_task(query(payload)))
    
    image_bytes_list = await asyncio.gather(*tasks)
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            image_path = os.path.join("Data", f"{prompt.replace(' ', '_')}_{i+1}.jpg")
            with open(image_path, "wb") as f:
                f.write(image_bytes)

def open_images(prompt):
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}_{i}.jpg" for i in range(1, 5)]
    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            img.show()
            sleep(1)
        except:
            pass

def GenerateImages(prompt: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_image(prompt))
    open_images(prompt)

file_path = r"Frontend\Files\ImageGeneration.data"
MAX_RETRIES = 5
retries = 0

while retries < MAX_RETRIES:
    data = get_file_data(file_path)
    if data:
        try:
            prompt, status = data.split(",", 1)
        except ValueError:
            retries += 1
            sleep(1)
            continue
        if status.strip() == "True":
            GenerateImages(prompt=prompt)
            update_file_status(file_path, "False,False")
        break
    else:
        retries += 1
        sleep(1)

if retries >= MAX_RETRIES:
    print("Max retries reached. Exiting...")
