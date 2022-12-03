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

print("Start Loading Json files in", __file__)

contents: dict = {}
with open("Content.json") as contents_file:
    contents = json.load(contents_file)

topics: dict = {}
with open("Topics.json") as topics_file:
    topics = json.load(topics_file)
    
submissions: dict = {}
with open("Submissions.json") as submissions_file:
    submissions = json.load(submissions_file)
    
submissions_meta: dict = {}
with open("Meta_Data_Submissions.json") as submissions_meta_file:
    submissions_meta = json.load(submissions_meta_file)
    
meta_data: dict = {}

removed_meta: dict = {}

print("Done Loading Json files in", __file__)

for sub_reddit in contents.keys():
    write_contents: dict = {}
    
    meta_data[sub_reddit] = {}
    removed_meta[sub_reddit] = {}
    for main_topic in contents[sub_reddit].keys():
        write_contents[sub_reddit] = {}
        
        content: list = []
        count = 0
        meta_data[sub_reddit][main_topic] = 0
        for submission in submissions[sub_reddit][main_topic]:
            if submission['keyword'] not in removed_meta[sub_reddit].keys():
                removed_meta[sub_reddit][submission['keyword']] = {"Actual": 0, "Deleted": 0, "Removed": 0, "Empty": 0}
            count += 1
            print("Comments for:", sub_reddit, "Topic:", main_topic, count, "/", submissions_meta[sub_reddit][main_topic], "with comments:", submission['num_comments'])
            gen = api.search_comments(link_id=submission['id'], subreddit=[sub_reddit],
                    filter=['id', 'subreddit', 'permalink', 'body', 'author', 'parent_id','score'], 
                    limit=submission['num_comments'])
            
            for item in gen:
                if item.body == "[deleted]":
                    removed_meta[sub_reddit][submission['keyword']]["Deleted"] += 1
                elif item.body == "[removed]":
                    removed_meta[sub_reddit][submission['keyword']]["Removed"] += 1
                elif item.body == "":
                    removed_meta[sub_reddit][submission['keyword']]["Empty"] += 1
                else:
                    removed_meta[sub_reddit][submission['keyword']]["Actual"] += 1

                item_dict = item.d_
                item_dict['topic'] = main_topic
                item_dict['created_time'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(item_dict['created']))
                item_dict['full_link'] = "https://www.reddit.com"
                if "permalink" in item_dict.keys():
                    item_dict['full_link'] += item_dict['permalink']
                item_dict['is_submission'] = False
                item_dict['keyword'] = submission['keyword']
                content.append(item_dict)
            
        meta_data[sub_reddit][main_topic] = len(content)
        
        # contents[sub_reddit][main_topic] = content
        write_contents[sub_reddit][main_topic] = content
        
        with open("Comments/Comments_" + sub_reddit + "_" + main_topic + ".json", "w+") as comments_file:
            json.dump(write_contents, comments_file, indent=2, sort_keys=True)
    
# print("Shards: ", api.metadata_.get('shards'))
# print("Meta_Data:", meta_data)

with open("Comments.json", "w+") as comments_file:
    json.dump(contents, comments_file, indent=2, sort_keys=True)
    
with open("Meta_Data_Comments.json", "w+") as meta_file:
    json.dump(meta_data, meta_file, indent=2, sort_keys=True)
    
with open("Meta_Data_Removed.json", "w+") as meta_removed_file:
    json.dump(removed_meta, meta_removed_file, indent=2, sort_keys=True)