# Zabbix Dovecot LLD stats

## linux
  * install zabbix-agent
    * (Centos/Rocky):
      * dnf install -y zabbix-agent
      * systemctl enable zabbix-agent
      * systemctl start zabbix-agent
  * allow FW zabbix-agent port (10050/TCP)
  * Python 3
    * mysql-connector-python
    * requests
  * MySQL / MariaDB:
    * create database, tables, user
  * script:
    * edit config 

## dovecot
```
#/etc/dovecot/dovecot.conf

doveadm_api_key = ***

service doveadm {
   unix_listener doveadm-server {
      user = vmail
   }
   inet_listener {
       port = 2425
   }
   inet_listener http {
       port = 8080
   }
}

#restart dovecot
#curl test:
#curl -H 'Authorization: X-Dovecot-API ***BASE64PWD***' -H 'Content-Type: application/json' -H "Content-type: application/json" -d '[["mailboxStatus",{"allUsers":true,"field":["all"],"mailboxMask":["*"]},"tag1"]]' 'http://127.0.0.1:8080/doveadm/v1'
#read test
#python3 /opt/dovecot_zabbix_lld/main.py lld
```

## create SQL database
```
CREATE DATABASE IF NOT EXISTS `zabbix_dovecot_stats` /*!40100 DEFAULT CHARACTER SET utf8mb3 COLLATE utf8mb3_czech_ci */;
USE `zabbix_dovecot_stats`;

CREATE TABLE IF NOT EXISTS `info` (
  `id` int(11) NOT NULL,
  `last_update` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_czech_ci;


CREATE TABLE IF NOT EXISTS `mailboxes` (
  `id` varchar(100) COLLATE utf8mb3_czech_ci NOT NULL,
  `vsize` bigint(20) NOT NULL,
  `messages` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_czech_ci;

CREATE USER 'stats'@localhost IDENTIFIED BY '*****';
GRANT ALL PRIVILEGES ON zabbix_dovecot_stats.* TO 'stats'@localhost;
FLUSH PRIVILEGES;
```

## agent config
```
UserParameter=dovecot.users.discovery,python3 /opt/dovecot_zabbix/main.py lld
UserParameter=dovecot.mailboxes.vsize[*],python3 /opt/dovecot_zabbix/main.py vsize $1
UserParameter=dovecot.mailboxes.messages[*],python3 /opt/dovecot_zabbix/main.py messages $1
```