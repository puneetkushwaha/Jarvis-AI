from Frontend.GUI import (
    GraphicalUserInterface, SetAssistantStatus, ShowTextToScreen, 
    TempDirectoryPath, SetMicrophoneStatus, AnswerModifier, QueryModifier, 
    GetMicrophoneStatus, GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
AssistantName = env_vars.get("Assistantname")

DefaultMessages = f"""{Username}: Hello {AssistantName}, How are you?
{AssistantName} : Welcome {Username}. I am doing well. How may I help you?"""

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
        if len(file.read()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as db_file:
                db_file.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as res_file:
                res_file.write(DefaultMessages)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = "User" if entry["role"] == "user" else "Assistant"
        formatted_chatlog += f"{role}: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username).replace("Assistant", AssistantName)
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
        data = file.read()
        if len(data) > 0:
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as res_file:
                res_file.write(data)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen(" ")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    
    print(f"\nDecision: {Decision}\n")
    
    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    
    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True
    
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True
    
    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
    
    if any(i.startswith("realtime") for i in Decision):
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{AssistantName}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    
    for Queries in Decision:
        if "general" in Queries:
            SetAssistantStatus("Thinking...")
            QueryFinal = Queries.replace("general", "")
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{AssistantName}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True
        
        elif "realtime" in Queries:
            SetAssistantStatus("Searching...")
            QueryFinal = Queries.replace("realtime", "")
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{AssistantName}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True
        
        elif "exit" in Queries:
            QueryFinal = "Okay, Bye!"
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{AssistantName}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available ..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ...")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
