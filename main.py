import sys
import requests
import json
import datetime
from collections import defaultdict
import base64
import copy
import mysql.connector as database
from config import CONFIG


def connect_db():
    connection = database.connect(
        user=CONFIG["db_connection"]["user"],
        password=CONFIG["db_connection"]["pwd"],
        host=CONFIG["db_connection"]["host"],
        database=CONFIG["db_connection"]["db"],
        port=CONFIG["db_connection"]["port"]
    , autocommit=False)
    return connection


def http_get_dovecot_mailboxes() -> str:
    headers = copy.deepcopy(CONFIG["dovecot"]["headers"])
    pwd = bytes(base64.b64encode(CONFIG["dovecot"]["pwd"].encode())).decode()
    headers["Authorization"] = headers["Authorization"].format(pwd=pwd)
    response_raw = requests.post(CONFIG["dovecot"]["url"], headers=headers, json=json.loads(CONFIG["dovecot"]["requests"]["get_mailbox_stat_all"]))
    response_conv = response_raw.content.decode('utf-8')
    return json.loads(response_conv)[0][1]


def assemble_mailboxes(data):
    mailboxes = defaultdict(lambda: {'vsize' : 0, 'messages' : 0})
    for i in data:
        mailboxes[i["username"]]["vsize"] += int(i["vsize"])
        mailboxes[i["username"]]["messages"] += int(i["messages"])

    mailboxes_list = [{'username' : k, "vsize" : v["vsize"], "messages" : v["messages"]} for k, v in mailboxes.items()]
    return mailboxes_list


def refresh_db_data(conn : database.MySQLConnection):
    with conn.cursor(buffered=True) as cursor:
        cursor.execute(CONFIG["queries"]["get_last_update"])
        last_update = cursor.fetchall()
        if (len(last_update) == 1) and (datetime.datetime.now().timestamp() - last_update[0][0].timestamp() < CONFIG["cache"]["max_cache_age"]):
            return

        mailboxes = http_get_dovecot_mailboxes()
        mailboxes_as = assemble_mailboxes(mailboxes)

        try:
            cursor.execute(CONFIG["queries"]["update_last_update"])
            for i in mailboxes_as:
                statement = CONFIG["queries"]["update_mailbox_info"].format(username=i["username"], vsize=i["vsize"], messages=i["messages"])
                cursor.executemany(statement, mailboxes_as)
        except:
            conn.rollback()
        else:
            conn.commit()


def return_lld():
    conn =  connect_db()
    refresh_db_data(conn)

    cursor = conn.cursor()
    cursor.execute(CONFIG["queries"]["get_usernames"])
    usernames = cursor.fetchall()
    result = [{CONFIG["lld"]["username_macro"]: i[0]} for i in usernames]
    print(json.dumps(result, separators=(',', ':')))


def return_user_param(name : str, param : str):
    if not param in CONFIG["allowed_user_params"]:
        return

    conn =  connect_db()
    refresh_db_data(conn)
    cursor = conn.cursor()
    cursor.execute(CONFIG["queries"]["get_user_vsize"].format(username=name, param=param))
    res = cursor.fetchall()

    if len(res) == 1:
        print(res[0][0])
    else:
        print(-1)


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'lld':
        return_lld()
    elif len(sys.argv) == 3 and(sys.argv[1] == 'vsize'):
        return_user_param(sys.argv[2], 'vsize')
    elif len(sys.argv) == 3 and (sys.argv[1] == 'messages'):
        return_user_param(sys.argv[2], 'messages')
    else:
        print("Invalid arguments:");
        print(sys.argv)
        exit(1)

if __name__ == '__main__':
    main()