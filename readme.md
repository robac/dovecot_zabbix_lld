# Zabbix Dovecot LLD stats

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