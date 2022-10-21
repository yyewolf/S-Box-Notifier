from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
import os

@dataclass
class Scan:
    keys: int = 0
    timer: int = 0
    people_in: int = 0
    people_watching: int = 0
    winner: str = ""
    

    def valid(self) -> bool:
        # we want it to be valid from 9 to 10 minutes, then from 4 to 5 minutes for another ping
        return (self.timer >= 9*60 and self.timer <= 10*60) or (self.timer >= 4*60 and self.timer <= 5*60)

class KeyScanner:
    def __init__(self, website_url:str, discord_webhook_url:str, log_url:str, headless:bool=False):
        self.webhook_url = discord_webhook_url
        self.website_url = website_url
        self.log_url = log_url
        self.scans = 0
        self.last_ping = 0
        self.checker = [0,0]
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=self.chrome_options)
    
    def notify(self, keys):
        message = f"Raffle will soon begin, there are {keys} keys available.\nClick [here]({self.website_url}) to go to the website."
        embed = {
            "title": "Key Drop",
            "description": message,
            "color": 0x00ff00,
            "footer": {
                "text": "Key Notifier - Yewolf"
            }
        }
        try:
            requests.post(self.webhook_url, json={"content":"@everyone","embeds": [embed]})
        except:
            pass

    def parse(self, time:str):
        # exemple : 5h 30m 0s => 19800s
        time = time.split(" ")
        hours = int(time[0].replace("h", ""))
        minutes = int(time[1].replace("m", ""))
        seconds = int(time[2].replace("s", ""))
        return hours*3600 + minutes*60 + seconds
    
    def format(self, time:int):
        hours = time // 3600
        minutes = (time % 3600) // 60
        seconds = time % 60
        return f"{hours}h {minutes}m {seconds}s"

    def analyze(self) -> Scan:
        scan = Scan()
        elems = self.driver.find_elements(By.CLASS_NAME, "tag")
        try:
            scan.keys = int(elems[0].text.split("\n")[-1])
            # parse the time %H %M %S to seconds
            scan.timer = self.parse(elems[1].text.split("\n")[-1])
            ## rotates checker
            self.checker[1] = self.checker[0]
            self.checker[0] = scan.timer
            scan.people_in = elems[2].text.split("\n")[-1]
            scan.people_watching = elems[3].text.split("\n")[-1]
            scan.winner = elems[4].text.split("\n")[-1]
        except:
            pass

        if scan.winner != "":
            log = {
                "title": "Winner",
                "color": 0x00ff00,
                "description": f"There has been a winner, {scan.winner} won a key !",
                "footer": {
                    "text": "Key Notifier - Yewolf"
                }
            }
            try:
                requests.post(self.log_url, json={"embeds": [log]})
            except:
                pass
        return scan
    
    def scan(self):
        if self.checker[0] == self.checker[1]:
            self.driver.get(self.website_url)
            time.sleep(1)
        scan = self.analyze()
        # checks the button "enter"
        if scan.valid() and time.time() - self.last_ping > 180:
            print("valid")
            self.notify(scan.keys)
            self.last_ping = time.time()
        self.scans += 1
    
    def start(self):
        while True:
            self.scan()
            time.sleep(1.5)


webhook_url = os.environ.get("WEBHOOK_URL", "")
log_url = os.environ.get("WEBHOOK_LOG_URL", "")
website_url = os.environ.get("WEBSITE_URL", "https://asset.party/get/developer/preview")

scanner = KeyScanner(website_url, webhook_url, log_url, False)
scanner.start()
