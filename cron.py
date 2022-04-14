import os
from config import CONFIG
from collections import defaultdict
import mysql.connector as database


def connect_db():
    connection = database.connect(
        user=CONFIG["db_connection"]["user"],
        password=CONFIG["db_connection"]["pwd"],
        host=CONFIG["db_connection"]["host"],
        database=CONFIG["db_connection"]["db"],
        port=CONFIG["db_connection"]["port"]
    , autocommit=False)
    return connection


def get_folder_size(path):
    total_size = 0
    total_messages = 0
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            size, messages = get_folder_size(entry.path)
            total_size += size
            total_messages += messages
        else:
            total_size += entry.stat(follow_symlinks=False).st_size
            total_messages += 1
    return total_size, total_messages


def count_mailboxes_data():
    mailboxes_data = defaultdict(lambda: {"vsize": 0, "messages": 0})
    for e in os.scandir(CONFIG["dovecot"]["users_folder"]):
        if e.is_dir():
            dirname = e.name
            size, messages = get_folder_size(e.path)
            mailboxes_data[dirname]["vsize"] += size
            mailboxes_data[dirname]["messages"] += messages
            mailboxes_data[dirname]["username"] = dirname

    return mailboxes_data


def refresh_db_data(conn : database.MySQLConnection):
    with conn.cursor(buffered=True) as cursor:
        mailboxes = count_mailboxes_data()

        try:
            cursor.execute(CONFIG["queries"]["update_last_update"])
            for key, m in mailboxes.items():
                statement = CONFIG["queries"]["update_mailbox_info"].format(username=m["username"], vsize=m["vsize"], messages=m["messages"])
                cursor.execute(statement)
        except Exception as e:
            conn.rollback()
            print(e)
        else:
            conn.commit()


def main():
    with connect_db() as conn:
        refresh_db_data(conn)

main()