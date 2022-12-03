import json
import os
import pysolr
import requests

CORE_NAME = "IRF22P4"
AWS_IP = "localhost"

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
    
comments: dict = {}
with open("Comments.json") as comments_file:
    comments = json.load(comments_file)
    
print("Done Loading Json files in", __file__)


def delete_core(core=CORE_NAME):
    print(os.system('sudo su - solr -c "/opt/solr/bin/solr delete -c {core}"'.format(core=core)))


def create_core(core=CORE_NAME):
    print(os.system(
        'sudo su - solr -c "/opt/solr/bin/solr create -c {core} -n data_driven_schema_configs"'.format(
            core=core)))


class Indexer:
    def __init__(self):
        self.solr_url = f'http://{AWS_IP}:8983/solr/'
        self.connection = pysolr.Solr(self.solr_url + CORE_NAME, always_commit=True, timeout=5000000)
        self.solr_admin = self.solr_url +"admin/cores"

    def do_initial_setup(self):
        delete_core()
        create_core()

    def create_documents(self, input_dict: dict):
        for sub_reddit in contents.keys():
            for main_topic in contents[sub_reddit].keys():
                collection: list = []
                for input in input_dict[sub_reddit][main_topic]:
                    doc: dict = {}
                    doc['id'] = input['id']
                    doc['subreddit'] = input['subreddit']
                    doc['full_link'] = input['full_link']
                    doc['author'] = input['author']
                    doc['is_submission'] = input['is_submission']
                    doc['topic'] = input['topic']
                    doc['created_at'] = input['created_time']
                    
                    if doc['is_submission'] == True:
                        doc['title'] = input['title']
                        doc['selftext'] = input['selftext']
                    else:
                        doc['body'] = input['body']
                        doc['parent_id'] = input['parent_id']
                        doc['parent_body'] = input['parent_body']
                        
                    collection.append(doc)
                print(self.connection.add(collection))

    def reload_core(self, CORE_NAME):
        print(requests.get(self.solr_admin + f"?action=RELOAD&core={CORE_NAME}").json())

    def add_fields(self):
        data = {
            "add-field": [
                {
                    "name": "author",
                    "type": "string",
                    "multiValued": False
                },
                {
                    "name": "full_link",
                    "type": "string",
                    "multiValued": False
                }, {
                    "name": "selftext",
                    "type": "text_en",
                    "multiValued": False
                },
                {
                    "name": "subreddit",
                    "type": "string",
                    "multiValued": False
                },
                {
                    "name": "title",
                    "type": "string",
                    "multiValued": False
                },
                {
                    "name": "is_submission",
                    "type": "boolean",
                    "multiValued": False
                },
                {
                    "name": "topic",
                    "type": "string",
                    "multiValued": False
                },
                {
                    "name": "created_at",
                    "type": "pdate",
                    "multiValued": False
                },
                {
                    "name": "body",
                    "type": "text_en",
                    "multiValued": False
                },
                {
                    "name": "parent_id",
                    "type": "string",
                    "multiValued": False
                },
                {
                    "name": "parent_body",
                    "type": "text_en",
                    "multiValued": False
                },
            ]
        }

        print(requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json())


if __name__ == "__main__":
    i = Indexer()
    i.do_initial_setup()
    i.add_fields()
    i.reload_core(CORE_NAME)
    i.create_documents(submissions)
    i.create_documents(comments)
