from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zcubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSB YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfke", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Jarvis')}, You're a Coder."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])
    
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic = Topic.replace("Content", "").strip()
    ContentByAI = ContentWriterAI(Topic)
    file_path = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    
    OpenNotepad(file_path)
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNB'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
                return None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True

def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False
    

def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
    }
    if command in actions:
        actions[command]()
        return True
    return False

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open"):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close"):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play"):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content"):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))
        elif command.startswith("google search"):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command.startswith("youtube search"):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))
        elif command.startswith("system"):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        else:
            print(f"No Function Found for {command}")
    
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True