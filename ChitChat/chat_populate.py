import chitchat_dataset as ccc
import json

dataset = ccc.Dataset()

messages = list(ccc.MessageDataset())

# print(messages[:30])

CHITCHAT = "chitchat"
chitchat: dict = {CHITCHAT: []}

for index, message in enumerate(messages):
    if index == len(messages) - 1:
        break
    
    blob: dict = {}
    blob["text"] = message
    blob["reply"] = messages[index + 1]
    chitchat[CHITCHAT].append(blob)

with open("Chitchat.json", "w+") as chitchat_file:
    json.dump(chitchat, chitchat_file, indent=2, sort_keys=True)
