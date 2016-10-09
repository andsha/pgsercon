#!/usr/bin/env python

import subprocess, logging




def templates(ver):
    # shmall = None
    # shmmax = None
    # result = subprocess.Popen(["sysctl", "-a"], stdout=subprocess.PIPE, universal_newlines = True, bufsize = -1).communicate()[0]
    #
    # if result:
    #     for l in result.split('\n'):
    #         if shmall and shmmax:
    #             break
    #         if 'shmmax' in l:
    #             shmmax = int(l.split(':')[1].strip())
    #         elif 'shmall' in l:
    #             shmall = int(l.split(':')[1].strip())
    #
    # if shmall is None and shmmax is None:
    #     logging.error('Cannot read shmmax and shmall settings')
    #     return {}
    #
    # shmmax = shmmax / 1048576
    # shmall = shmall / 1048576
    #
    # if shmmax > 1024:
    #     shared = min(shmmax / 6, shmall / 3, 2048)
    # else:
    #     shared = min(shmmax / 8, shmall / 3)
    # if shared < 2:
    #     shared = 8
    # #logging.debug(shared)
    #
    # wal = 1
    # if (shmmax - shared) > 100:
    #     wal = 32
    # cache = shared * 2

    templates = {
        "Memory Allocations": {
            "max_locks_per_transaction": "__DEFAULT__",
            "wal_buffers" : "__DEFAULT__",
            "shared_buffers" : "__DEFAULT__",
            "effective_cache_size" : "__DEFAULT__",
            "work_mem" : "__DEFAULT__",
            "random_page_cost" : "__DEFAULT__",
            "maintenance_work_mem" : "__DEFAULT__",
            "checkpoint_completion_target" : "__DEFAULT__",
            "synchronous_commit" : "__DEFAULT__",
        },
        "Logging Settings": {
            "log_destination" : "stderr",
            "logging_collector" : "on",
            "log_directory" : "'pg_log'",
            "log_filename" : "'postgresql.log'",
            "log_rotation_age" : "0",
            "client_min_messages" : "notice",
            "log_min_messages" : "warning",
            "log_min_error_statement" : "error",
            "log_min_duration_statement" : "600000",
            "log_duration" : "off",
            "log_line_prefix" : "'%t %u %h '",
            "log_lock_waits" : "on",
            "log_statement" : "none",
            "DateStyle" : "'ISO, MDY'",
            "TimeZone" : "'GMT'",
            "lc_messages" : "'en_US.utf8'",
            "lc_monetary" : "'en_US.utf8'",
            "lc_numeric" : "'en_US.utf8'",
            "lc_time" : "'en_US.utf8'",
            "default_text_search_config" : "'pg_catalog.english'"
        },
        "General": {
            "listen_addresses" : "'*'",
            "port" : "5432",
            "max_connections" :"100",
            "external_pid_file" : "'{PIDFOLDER}/postmaster.pid'"
        },
        "Master": {
            "wal_level" : "hot_standby",
            "max_wal_senders" : "5",
            "archive_mode" : "on",
            "archive_command" : "'cp %p /tmp/pg_archive/%f'"
        },
        "Slave": {
            "hot_standby" : "on",
            "wal_level" : "hot_standby",
            "max_wal_senders" : "5"
        },
    }

    if ver != '9.2':
        templates["General"]["unix_socket_directories"] = "'{PIDFOLDER}'"

    return templates

