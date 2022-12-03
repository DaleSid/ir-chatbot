import json

SUBMISSIONS = "submissions"
COMMENTS = "comments"

print("Start Loading Json files in", __file__)

submissions_meta: dict = {}
with open("Meta_Data_Submissions.json") as submissions_meta_file:
    submissions_meta = json.load(submissions_meta_file)
    
comments_meta: dict = {}
with open("Meta_Data_Comments.json") as comments_meta_file:
    comments_meta = json.load(comments_meta_file)
    
print("Done Loading Json files in", __file__)

meta_subreddit: dict = {}
meta_topics: dict = {}

def gather_meta(data_type: str):
    meta: dict = {}
    if data_type == SUBMISSIONS:
        meta = submissions_meta
    else:
        meta = comments_meta

    for sub_reddit in meta.keys():
        if sub_reddit not in meta_subreddit.keys():
            meta_subreddit[sub_reddit] = {SUBMISSIONS: 0, COMMENTS: 0}
        for topic in meta[sub_reddit].keys():
            if topic not in meta_topics.keys():
                meta_topics[topic] = {SUBMISSIONS: 0, COMMENTS: 0}
                
            meta_topics[topic][data_type] += meta[sub_reddit][topic]
            meta_subreddit[sub_reddit][data_type] += meta[sub_reddit][topic]
            
gather_meta(SUBMISSIONS)
gather_meta(COMMENTS)

with open("Meta_Data_Subreddit.json", "w+") as meta_sureddit_file:
    json.dump(meta_subreddit, meta_sureddit_file, indent=2, sort_keys=True)
    
with open("Meta_Data_Topic.json", "w+") as meta_topic_file:
    json.dump(meta_topics, meta_topic_file, indent=2, sort_keys=True)