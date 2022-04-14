CONFIG = {
    "dovecot" : {
        "users_folder" : r'd:\\test\\xxx\\',
    },
    "db_connection" : {
        "host" : "127.0.0.1",
        "port" : 3307,
        "db" : "zabbix_dovecot_stats",
        "user" : "root",
        "pwd" : "example"
    },
    "queries" :{
        "get_last_update" : "SELECT last_update FROM info WHERE id = 1;",
        "update_last_update" : "INSERT INTO info (id, last_update) VALUES (1, now()) ON DUPLICATE KEY UPDATE last_update = now();",
        "update_mailbox_info" : "INSERT INTO mailboxes (id, vsize, messages) VALUES ('{username}', {vsize}, {messages}) ON DUPLICATE KEY UPDATE vsize = {vsize}, messages = {messages};",
        "get_usernames" : "SELECT id FROM mailboxes;",
        "get_user_vsize" : "SELECT {param} FROM mailboxes WHERE id = '{username}';",
    },
    "allowed_user_params" : ["vsize", "messages"],
    "cache" : {
        "max_cache_age" : 600,
    },
    "lld" : {
        "username_macro" : r"{#USERNAME}"
    }
}
