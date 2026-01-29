import time
from datetime import datetime

def auto_post_console(tweets: list[str], delay=1800):
    for t in tweets:
        print(f"[{datetime.now().strftime('%H:%M')}] {t}")
        time.sleep(delay)
