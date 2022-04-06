import sys
import requests
import json
import pprint
import os
import datetime

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

def load_http_data():
    response_raw = requests.post(REQUEST["url"], headers=REQUEST["headers"], json=json.loads(REQUEST["data"]))
    response_conv = response_raw.content.decode('utf-8')
    with open(CONFIG["temp_file"], 'w') as temp:
        temp.write(response_conv)
    return json.loads(response_conv)[0][1]

def get_dovecot_data():
    if os.path.exists(CONFIG["temp_file"]) and get_file_age_from_now(CONFIG["temp_file"]) < CONFIG["max_temp_age"]:
        try:
            with open(CONFIG["temp_file"], 'r') as temp:
                data = temp.read()
                response = json.loads(data)[0][1]
                return response
        except:
            pass

    return load_http_data()

def is_cache_valid():
    return os.path.exists(CONFIG["temp_file"]) and get_file_age_from_now(CONFIG["temp_file"]) < CONFIG["max_temp_age"]


def load_cache():
    with open(CONFIG["temp_file"], 'r') as temp:
        data = temp.read()
        response = json.loads(data)[0][1]
        return response


def get_dovecot_users():
    if is_cache_valid():
        try:
            return load_cache()
        except:
            pass

    return load_http_data(save=True)


def return_lld():
    usernames = {}
    dovecot_data = get_dovecot_data()
    for item in dovecot_data:
        username = item['username']
        if not username in usernames:
            usernames[username] = None

    result = []
    for username in usernames.keys():
        result.append({CONFIG["username_macro"] : username})

    result = sorted(result, key= lambda item : item[CONFIG["username_macro"]])
    print(json.dumps(result, separators=(',', ':')))

def return_vsize(name : str):
    name = name.strip().lower()
    dovecot_data = get_dovecot_data()
    vsize = 0
    for item in dovecot_data:
        username = item['username']
        if (username == name):
            vsize += int(item['vsize'])
    print(vsize)

def return_messages(name : str):
    name = name.strip().lower()
    dovecot_data = get_dovecot_data()
    messages = 0
    for item in dovecot_data:
        username = item['username']
        if (username == name):
            messages += int(item['messages'])
    print(messages)


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