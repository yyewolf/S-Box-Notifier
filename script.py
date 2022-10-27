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
        self.last_ping = 0
        self.poll_rate = 1.5
        self.winners = []
        self.checker = [0,0]
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=self.chrome_options)
    
    def notify(self, scan:Scan):
        message = f"Raffle will begin in {self.format(scan.timer)} there are {scan.keys} keys available.\nClick [here]({self.website_url}) to go to the website."
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

    def fast_near_loot(self, scan:Scan):
        if self.timer > 2:
            self.poll_rate = 0.5
        else:
            self.poll_rate = 1.5

    def analyze(self) -> Scan:
        scan = Scan()
        elems = self.driver.find_elements(By.CLASS_NAME, "tag")

        if len(elems) > 3:
            # parse keys available
            scan.keys = safe_cast(elems[0].text.split("\n")[-1], int, 0)
            # parse the time %H %M %S to seconds
            try:
                scan.timer = self.parse(elems[1].text.split("\n")[-1])
            except:
                scan.timer = 0
            # parse people in
            ## rotates checker
            self.checker[1] = self.checker[0]
            self.checker[0] = scan.timer
            # parse people in
            scan.people_in = elems[2].text.split("\n")[-1]
            # parse people watching
            scan.people_watching = elems[3].text.split("\n")[-1]
        if len(elems) > 4:
            # parse winners
            scan.winner = elems[4].text.split("\n")[-1]

        if scan.winner not in self.winners and scan.winner not in ["", "..."]:
            print("Winner found:", scan.winner)
            self.winners.append(scan.winner)
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
        if (self.checker[0] == self.checker[1] and self.poll_rate == 1.5) or 'refresh' in self.driver.page_source:
            print("Refreshing...")
            self.driver.get(self.website_url)
            time.sleep(1)
            
        scan = self.analyze()
        # checks the button "enter"
        print(scan)
        
        if scan.valid() and time.time() - self.last_ping > 180:
            self.notify(scan)
            self.last_ping = time.time()
    
    def start(self):
        while True:
            self.scan()
            time.sleep(self.poll_rate)

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

webhook_url = os.environ.get("WEBHOOK_URL", "")
log_url = os.environ.get("WEBHOOK_LOG_URL", "")
website_url = os.environ.get("WEBSITE_URL", "https://asset.party/get/developer/preview")

scanner = KeyScanner(website_url, webhook_url, log_url, True)
scanner.start()
