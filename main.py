import sys
import json
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


def return_lld():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(CONFIG["queries"]["get_usernames"])
        usernames = cursor.fetchall()
        result = [{CONFIG["lld"]["username_macro"]: i[0]} for i in usernames]
        print(json.dumps(result, separators=(',', ':')))


def return_user_param(name : str, param : str):
    if not param in CONFIG["allowed_user_params"]:
        return

    conn =  connect_db()
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