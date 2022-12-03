from flask import Flask, request
import json
import requests

app = Flask(__name__)

IP = "localhost"
url = "http://34.124.115.77:8983/solr/chitchat/query?fl=text, reply, score, topic"

@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'

@app.route('/send')
def send_message():
    payload: dict = dict(json.loads(request.get_data()))
    
    text = payload["text"]
    
    payload = json.dumps({
        "query": "text: " + text,
        "limit": 20
    })
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    ret: dict = process_message(response.json())
    return ret
    
def process_message(response: dict) -> dict:
    return response

if __name__ == "__main__":
    app.run(host=IP, port=9999, debug=True)