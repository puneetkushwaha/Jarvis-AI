from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time  

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")  

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;  // Fixed appending issue
            };

            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
        }
    </script>
</body>
</html>'''


HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")


os.makedirs("Data", exist_ok=True)
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)


current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"


chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new") 


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


def QueryModifier(Query):
    new_query = Query.strip().lower()
    if new_query[-1] not in ['.', '?', '!']:
        new_query += "?"
    return new_query.capitalize()


def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()


def SpeechRecognition():
    driver.get("file:///" + Link)
    driver.find_element(By.ID, "start").click()
    time.sleep(1)  

    while True:
        try:
            text = driver.find_element(By.ID, "output").text.strip()
            if text:
                driver.find_element(By.ID, "end").click()
                if "en" in InputLanguage.lower():
                    return QueryModifier(text)
                else:
                    return QueryModifier(UniversalTranslator(text))
        except Exception:
            time.sleep(0.5)  


if __name__ == "__main__":
    try:
        while True:
            Text = SpeechRecognition()
            print(Text)
    except KeyboardInterrupt:
        print("\nStopping Speech Recognition.")
    finally:
        driver.quit()  
