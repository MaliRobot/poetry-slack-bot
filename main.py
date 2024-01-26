from typing import List, Tuple
import os
from dotenv import load_dotenv

import logging
import requests

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


logging.basicConfig(level=logging.INFO)
load_dotenv()
poetrydb_url = os.environ['POETRYDB_URL']

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.event("app_mention")
def handle_app_mention_events(body, client):
    poetry_lines, new_last_line = get_random_poetry()
    client.chat_postMessage(
        channel=body["event"]["channel"],
        text=f"Hi <@{body['event']['user']}>. I'm a poetry bot. I bring you poems such as this one:\n```{poetry_lines}```",
    )

@app.message()
def handle_message(message, say):
    text = message.get("text")
    poetry_lines, new_last_line = get_poetry(text)
    if poetry_lines:
        say(poetry_lines)


def poem_from_lines(lines: List[str], search: str = None) -> Tuple[str, str]:
    if search:
        # search term should be in the first line of response
        for e, line in enumerate(lines):
            if search in line:
                lines = lines[e:]

    if '' in lines:
        # This is to shorten a poem a bit as some of them can be too long
        idx = lines.index('')
        if idx:
            lines = lines[:idx]

    return '\n'.join(lines), lines[-1]


def get_poetry(search: str):
    url = f"https://poetrydb.org/lines,poemcount/{search};1/lines"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            lines = data[0].get('lines')
            if lines:
                return poem_from_lines(lines, search)
    return None, None


def get_random_poetry():
    url = f"https://poetrydb.org/random/1/lines"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            lines = data[0].get('lines')
            if lines:
                return poem_from_lines(lines)
    return None, None


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
