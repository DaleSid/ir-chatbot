import random

from flask import Flask, request
import json
import requests
import logging

logger = logging.getLogger()

app = Flask(__name__)

IP = "localhost"
url = "http://34.124.115.77:8983/solr/chitchat/query?fl=text, reply, score, topic"


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/send', methods=['POST'])
def send_message():
    payload: dict = dict(json.loads(request.get_data()))
    
    text = payload["text"]
    topics = payload["topics"]

    filters = ""
    if topics != "All":
        list_topics: list = ["topic:" + topic for topic in topics]
        filters = ' OR '.join(list_topics)

    payload = json.dumps({
        "query": "text: " + text.replace(" ", "+"),
        "limit": 20,
        "filter": [
            filters
        ]
    })
    
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    ret: dict = get_processed_message(response.json())

    return ret


def get_processed_message(response: dict) -> dict:
    if not response.get("response").get("numFound"):
        return {
            "reply": "Sorry!!! couldn't able to find what you are looking for. Try something else",
            "score": 0,
            "text":  "",
            "topic": "",
            "status": False
        }
    docs = response.get("response").get("docs")
    sorted_docs = sorted(docs, key=lambda d: d['score'], reverse=True)
    if len(sorted_docs) > 5:
        sorted_docs = sorted_docs[:5]
    final_response = random.choice(sorted_docs)
    final_response["status"] = True

    return final_response


if __name__ == "__main__":
    app.run(host=IP, port=9999, debug=True)