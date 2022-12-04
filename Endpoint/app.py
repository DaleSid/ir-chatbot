import random

from flask import Flask, request
import json
import requests
import logging

import torch
import json
import numpy as np
from transformers import BertTokenizer
from torch import nn
from transformers import BertModel

logger = logging.getLogger()

app = Flask(__name__)

IP = "localhost"
url = "http://34.124.115.77:8983/solr/chitchat/query?fl=text, reply, score, topic"

class BertClassifier(nn.Module):

    def __init__(self, dropout=0.5):

        super(BertClassifier, self).__init__()

        self.bert = BertModel.from_pretrained('bert-base-cased')
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, 2)
        self.relu = nn.ReLU()

    def forward(self, input_id, mask):

        _, pooled_output = self.bert(input_ids= input_id, attention_mask=mask,return_dict=False)
        dropout_output = self.dropout(pooled_output)
        linear_output = self.linear(dropout_output)
        final_layer = self.relu(linear_output)

        return final_layer

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
        list_topics: list = ["topic:" + topic for topic in topics.split(',')]
        filters = ' OR '.join(list_topics)

    # print(find_type(text))
    if(find_type(text) == 'chitchat'):
        filters = "topic:chitchat"
    
    payload = json.dumps({
        "query": "text: " + text,
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

def find_type(text: str):
    labels = {
        'reddit':0,
        'chitchat':1
    }
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    texts = tokenizer(text, 
                    padding='max_length', max_length = 512, truncation=True,
                    return_tensors="pt")
    mask = texts['attention_mask'].to(device)
    input_id = texts['input_ids'].squeeze(1).to(device)

    output = model(input_id, mask)
    # print('Query:', text)
    # print(list(labels.keys())[(torch.argmax(output).item())])
    return list(labels.keys())[(torch.argmax(output).item())]

def get_processed_message(response: dict) -> dict:
    docs = response.get("response").get("docs")
    sorted_docs = sorted(docs, key=lambda d: d['score'], reverse=True)
    if len(sorted_docs) > 5:
        sorted_docs = sorted_docs[:5]
    final_response = random.choice(sorted_docs)

    return final_response


if __name__ == "__main__":
    tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
    model = BertClassifier()
    model.load_state_dict(torch.load('../ML/binary_bert_model.pt',map_location=torch.device('cpu')))
    model.eval()
    app.run(host=IP, port=9999, debug=True)