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
    time: int = 0
    keys: int = 0
    tags: int = 0
    enabled: bool = False
    people: int = 0

    def valid(self) -> bool:
        return self.enabled

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
        message = f"Key drop at : {time.strftime('%H:%M:%S')}, there are {keys} keys available.\nClick [here]({self.website_url}) to go to the website."
        embed = {
            "title": "Key Drop",
            "description": message,
            "color": 0x00ff00,
            "footer": {
                "text": "Key Notifier - Yewolf"
            }
        }
        requests.post(self.webhook_url, json={"content":"@everyone","embeds": [embed]})

    def analyze(self) -> Scan:
        scan = Scan()
        elems = self.driver.find_elements(By.CLASS_NAME, "tag")
        btns = self.driver.find_elements(By.CLASS_NAME, "button")
        scan.tags = len(elems)
        try:
            if btns[0].text == "enter":
                scan.enabled = btns[0].is_enabled()
            scan.keys = elems[0].text.split("\n")[-1]
            scan.people = elems[-1].text.split("\n")[-1]
        except:
            pass

        log = {
            "title": "Scanned",
            "color": 0x00ff00,
            "description": f"Time: {time.strftime('%H:%M:%S')}\nTotal scans: {self.scans}\nKeys: {scan.keys}\nPeople: {scan.people}\nButton Enabled: {scan.enabled}",
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


webhook_url = os.environ.get("WEBHOOK_URL")
log_url = os.environ.get("WEBHOOK_LOG_URL")
website_url = os.environ.get("WEBSITE_URL")
poll_rate = int(os.environ.get("POLL_RATE", 60))

scanner = KeyScanner(website_url, webhook_url, log_url, poll_rate, True)
scanner.start()