import json
import os
import time

from bs4 import BeautifulSoup
from requests import session
from langdetect import detect, LangDetectException
import re

from secret import MAIL_SAVE_DIR, CRAWLER_PROG_DIR, MAX_PAGE

URL = "http://scamletters.info/category/scam/page/__page__"

EMAIL_RE = re.compile(r"\w+?@\w+?\.\w+")
s = session()

if not os.path.exists(MAIL_SAVE_DIR):
    os.makedirs(MAIL_SAVE_DIR)

if not os.path.exists(CRAWLER_PROG_DIR):
    os.makedirs(CRAWLER_PROG_DIR)

PROG_FILE = CRAWLER_PROG_DIR + "/sli.his"


def get_info_list(page=1):
    res = s.get(URL.replace("__page__", str(page)))
    if not res.ok:
        return False, []

    info_list = []

    soup = BeautifulSoup(res.text, "lxml")

    progress_saved = False

    last_url = None
    if os.path.exists(PROG_FILE):
        with open(PROG_FILE, "r", encoding="utf8") as f:
            prog = json.load(f)
            last_url = prog["last_url"]
    count = 0
    early_stop = False

    for article in soup.select("article"):
        header_a = article.header.h2.a
        # preview_text = article.find("p").get_text(strip=True).replace("\xa0", " ")
        date = str(article.find("div", class_="autor-fecha").contents[6]).strip()

        url = header_a["href"]
        if url == last_url:
            # print("The article has been fetched, stopping..")
            early_stop = True
            break

        info = {
            "title": header_a.get_text(),
            "url": url,
            "date": date
        }
        info_list.append(info)
        count += 1

        if not progress_saved and page == 1:
            progress_saved = True
            prog = {"last_url": info["url"], "time": time.time()}
            with open(PROG_FILE, "w", encoding="utf8") as f:
                json.dump(prog, f)
    if len(info_list) > 0:
        print(f"Found {len(info_list)} scam letters in page {page}")
    return early_stop, info_list


def get_body(info):
    url = info["url"]
    file_name = url.rsplit("/", 2)[1]
    output_path = f"{MAIL_SAVE_DIR}/{file_name}.json"
    if os.path.exists(output_path):
        return

    res = s.get(url)
    if res.ok:
        soup = BeautifulSoup(res.text, "lxml")
        content = soup.find("div", class_="entry-content").text.strip()

        try:
            if detect(content) != 'en':
                return
        except LangDetectException:
            return

        info["content"] = content

        match = re.search(EMAIL_RE, content)
        if match:
            info["from"] = match.group(0).lower()
        else:
            print(f"Cannot find email addr in {url}")
            return

        with open(output_path, "w", encoding="utf8") as f:
            json.dump(info, f, indent=4)


def fetch():
    # print("Start to fetch scamletter.info")
    final_info_list = []
    for i in range(1, MAX_PAGE + 1):
        # print(f"Fetching page {i}")
        early_stop, info_list = get_info_list(i)
        final_info_list.extend(info_list)

        if early_stop:
            break
    for info in final_info_list:
        get_body(info)


def main():
    fetch()


if __name__ == '__main__':
    main()
