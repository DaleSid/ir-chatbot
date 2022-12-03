import json
import time
from psaw import PushshiftAPI
import logging
api = PushshiftAPI()

logging.basicConfig(filename="comments.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

SUBMISSIONS_LIMIT = 5

print("Start Loading Json files in", __file__)

contents: dict = {}

with open("Content.json") as contents_file:
    contents = json.load(contents_file)

topics: dict = {}
with open("Topics.json") as topics_file:
    topics = json.load(topics_file)
    
meta_data: dict = {}
    
print("Done Loading Json files in", __file__)

for sub_reddit in contents.keys():
    meta_data[sub_reddit] = {}
    for main_topic in topics.keys():
        content: list = []
        meta_data[sub_reddit][main_topic] = 0
        for topic in topics[main_topic]:
            print("For sub_reddit:", sub_reddit, "with main topic:", main_topic, "and sub topic:", topic)
            query = {
                "q": topic,
                "before": "1y",
                "subreddit": [sub_reddit],
                "num_comments": ">3",
                "selftext": topic,
                "selftext:not": "[removed]|[deleted]",
                "filter": ['id', 'subreddit', 'full_link', 'title', 'selftext', 'author', 'score', 'num_comments'],
                "limit": SUBMISSIONS_LIMIT
            }
            
            if sub_reddit == "FoodForThought":
                query.pop("selftext")
            
            gen = api.search_submissions(**query)
            for item in gen:
                # if item.selftext != "[deleted]" and item.selftext != "[removed]":
                item_dict = item.d_
                item_dict['topic'] = main_topic
                item_dict['created_time'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(item_dict['created']))
                item_dict['is_submission'] = True
                item_dict['keyword'] = topic
                if "selftext" in item_dict.keys():
                    text = item_dict['selftext']
                else:
                    text = ""
                item_dict['selftext'] = text
                content.append(item_dict)
            
        contents[sub_reddit][main_topic] = content
        meta_data[sub_reddit][main_topic] = len(content)
    
print("Shards:", api.metadata_.get('shards'))
# print("Meta_Data:", meta_data)

with open("Submissions.json", "w+") as submissions_file:
    json.dump(contents, submissions_file, indent=2, sort_keys=True)
    
with open("Meta_Data_Submissions.json", "w+") as meta_file:
    json.dump(meta_data, meta_file, indent=2, sort_keys=True)