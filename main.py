import sys
import requests
import json
import pprint
import os
import datetime
from collections import defaultdict

CONFIG = {
    "temp_file" : "cache.txt",
    "max_temp_age" : 300,
    "username_macro" : r"{#USERNAME}"
}

REQUEST = {
    "url" : r'http://172.30.128.189:8080/doveadm/v1',
    "headers" : {
        "Authorization" : "X-Dovecot-API a2V5",
        "Content-Type" : "application/json"
    },
    "data" : r'[["mailboxStatus",{"allUsers":true,"field":["all"],"mailboxMask":["*"]},"tag1"]]'
}


def get_file_age_from_now(filename : str) -> int:
    file_age = os.path.getmtime(CONFIG["temp_file"])
    now = datetime.datetime.now().timestamp()
    return(int(now - file_age))


def load_http_data() -> str:
    response_raw = requests.post(REQUEST["url"], headers=REQUEST["headers"], json=json.loads(REQUEST["data"]))
    response_conv = response_raw.content.decode('utf-8')
    return json.loads(response_conv)


def is_cache_valid() -> bool:
    return os.path.exists(CONFIG["temp_file"]) and get_file_age_from_now(CONFIG["temp_file"]) < CONFIG["max_temp_age"]


def assemble_users(data):
    used = set()
    usernames = [i["username"] for i in data if (i["username"] not in used) and (used.add(i["username"]) or True)]
    usernames.sort()
    return usernames


def assemble_mailboxes(data):
    mailboxes = defaultdict(lambda: {'vsize' : 0, 'messages' : 0})
    for i in data:
        mailboxes[i["username"]]["vsize"] += int(i["vsize"])
        mailboxes[i["username"]]["messages"] += int(i["messages"])
    return mailboxes



def get_dovecot_data(save : bool = True):
    if is_cache_valid():
        try:
            with open(CONFIG["temp_file"], 'r') as temp:
                usernames = json.loads(temp.readline())
                mailboxes = json.loads(temp.readline())
        except:
            pass
        else:
            return usernames, mailboxes

    data = load_http_data()[0][1]
    usernames = assemble_users(data)
    mailboxes = assemble_mailboxes(data)
    if (save):
        with open(CONFIG["temp_file"], 'w') as temp:
            temp.write(json.dumps(usernames, separators=(',', ':'))+"\n")
            temp.write(json.dumps(mailboxes, separators=(',', ':')))
    return usernames, mailboxes


def return_lld():
    usernames, _ = get_dovecot_data()
    result = [{CONFIG["username_macro"] : i} for i in usernames]
    print(json.dumps(result, separators=(',', ':')))

def return_vsize(name : str):
    name = name.strip().lower()
    _, mailboxes = get_dovecot_data()

    if (name in mailboxes):
        print(mailboxes[name]['vsize'])
    else:
        print(-1)

def return_messages(name : str):
    name = name.strip().lower()
    _, mailboxes = get_dovecot_data()

    if (name in mailboxes):
        print(mailboxes[name]['messages'])
    else:
        print(-1)


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'lld':
        return_lld()
    elif len(sys.argv) == 3 and(sys.argv[1] == 'vsize'):
        return_vsize(sys.argv[2])
    elif len(sys.argv) == 3 and (sys.argv[1] == 'messages'):
        return_messages(sys.argv[2])
    else:
        print("Invalid arguments:");
        print(sys.argv)
        exit(1)

if __name__ == '__main__':
    main()