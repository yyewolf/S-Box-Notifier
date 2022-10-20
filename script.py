from asyncore import poll
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
    

    def valid(self) -> bool:
        # we want it to be valid from 12 to 8 minutes, then from 6 to 2 minutes for another ping
        return (self.timer >= 720 and self.timer <= 480) or (self.timer >= 360 and self.timer <= 120)

class KeyScanner:
    def __init__(self, website_url:str, discord_webhook_url:str, log_url:str, poll_rate:int, headless:bool=False):
        self.webhook_url = discord_webhook_url
        self.website_url = website_url
        self.log_url = log_url
        self.poll_rate = poll_rate
        self.validscans = []
        self.scans = 0
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def add_status(self, scan:Scan):
        self.validscans.append(scan)

    def last_status(self) -> Scan:
        if len(self.validscans) > 0:
            return self.validscans[-1]
        return Scan()
    
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
        requests.post(self.webhook_url, json={"content":"@everyone","embeds": [embed]})

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
            scan.people_in = elems[2].text.split("\n")[-1]
            scan.people_watching = elems[3].text.split("\n")[-1]
        except:
            pass

        log = {
            "title": "Scanned",
            "color": 0x00ff00,
            "description": f"Keys: {scan.keys}\nTimer: {self.format(scan.timer)}\nPeople In: {scan.people_in}\nPeople Watching: {scan.people_watching}\nTotal scans: {self.scans}",
            "footer": {
                "text": "Key Notifier - Yewolf"
            }
        }
        requests.post(self.log_url, json={"embeds": [log]})
        return scan
    
    def scan(self):
        self.driver.get(self.website_url)
        time.sleep(1)
        scan = self.analyze()
        # checks the button "enter"
        if scan.valid() and time.time() - self.last_status().time > 180:
            self.notify(scan.keys)
            self.add_status(scan)
        self.scans += 1
    
    def start(self):
        while True:
            self.scan()
            time.sleep(self.poll_rate-1)


webhook_url = os.environ.get("WEBHOOK_URL", "")
log_url = os.environ.get("WEBHOOK_LOG_URL", "")
website_url = os.environ.get("WEBSITE_URL", "https://asset.party/get/developer/preview")
poll_rate = int(os.environ.get("POLL_RATE", 60))

scanner = KeyScanner(website_url, webhook_url, log_url, poll_rate, True)
scanner.start()
