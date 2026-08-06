from vidsift.features.logs.log_viewer import LogViewer
from vidsift.models.log_criteria import LogCriteria


def register_logs(subparsers):
    logs_parser = subparsers.add_parser(
        "logs",
        help="View and filter vidsift log files",
    )

    line_number_exclusive = logs_parser.add_mutually_exclusive_group()
    line_number_exclusive.add_argument(
        "--follow",
        action="store_true",
        help="Follow the log file and print new log entries as they are written",
    )

    logs_parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Only show log entries at or above this level, default: INFO",
        default="INFO",
    )

    logs_parser.add_argument(
        "--contains",
        help="Only show log entries whose message contains this text",
        default="",
    )

    line_number_exclusive.add_argument(
        "--last",
        type=int,
        metavar="N",
        help="Only show the last N log entries, default: 20",
        default=20,
    )

    logs_parser.add_argument(
        "--format",
        nargs="+",
        help="""Format the log output. 
Variables: $timestamp, $level, $run_id, $event, $logger, $message
Default format: $timestamp $run_id $level: $event $message
""",
        default=["$timestamp", "$run_id", "$level:", "$event", "$message"],
    )

    logs_parser.add_argument("--starttime", help="From when the logs should be.")
    logs_parser.add_argument("--endtime", help="Until when the logs should be.")

    logs_parser.set_defaults(func=handle_logs)

    return logs_parser


def handle_logs(args, config):
    viewer = LogViewer(
        config=config,
        log_criteria=LogCriteria(
            level=args.level,
            contains=args.contains,
            last=args.last,
            format=args.format,
            starttime=args.starttime,
            endtime=args.endtime,
        ),
    )

    if args.follow:
        viewer.follow()
        return

    viewer.show()
