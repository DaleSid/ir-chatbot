#!/bin/sh
pip3 install chitchat_dataset
python3 chat_populate.py
python3 Indexer.py