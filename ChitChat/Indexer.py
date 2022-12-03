import json
import os
import pysolr
import requests

CORE_NAME = "chitchat"
AWS_IP = "localhost"

print("Start Loading Json files in", __file__)

contents: dict = {}
with open("Chitchat.json") as contents_file:
    contents = json.load(contents_file)
    
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
        collection = input_dict["chitchat"]
        print(self.connection.add(collection))

    def reload_core(self, CORE_NAME):
        print(requests.get(self.solr_admin + f"?action=RELOAD&core={CORE_NAME}").json())

    def add_fields(self):
        data = {
            "add-field": [
                {
                    "name": "text",
                    "type": "text_en",
                    "multiValued": False
                },
                {
                    "name": "reply",
                    "type": "text_en",
                    "multiValued": False
                }
            ]
        }

        print(requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json())


if __name__ == "__main__":
    i = Indexer()
    i.do_initial_setup()
    i.add_fields()
    i.reload_core(CORE_NAME)
    i.create_documents(contents)
