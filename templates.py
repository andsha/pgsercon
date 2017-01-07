#!/usr/bin/env python


def templates(ver, defaults):




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

