from argparse import ArgumentParser

import argcomplete

from vidsift.cli.commands.config import register_config
from vidsift.cli.commands.init import register_init
from vidsift.cli.commands.logs import register_logs
from vidsift.cli.commands.process import register_process
from vidsift.cli.commands.run import register_run
from vidsift.cli.commands.schedule import register_schedule
from vidsift.cli.commands.service import register_service
from vidsift.cli.commands.videos import register_videos


def parse_args():
    parser = ArgumentParser(
        prog="vidsift",
        suggest_on_error=True,
        description="""AI-powered YouTube feed filtering and transcript-based video validation and processing""",
    )

    parser.add_argument(
        "-V",
        "--version",
        help="Print version",
        action="version",
        version="vidsift v0.0.1",
    )
    parser.add_argument(
        "--config",
        help="Use custom config for this run",
    ).completer = argcomplete.completers.FilesCompleter
    parser.add_argument(
        "--loglevel",
        help="Set the loglevel console logging for one run",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument("--global-ai-model", help="Set the AI model for all AI usages")

    parser.add_argument(
        "--skip-ai-checks",
        help="Skip checks for AI availibility and existence, not recommended for running in the background",
        action="store_true",
    )

    parser.add_argument(
        "--debug",
        help="Debug vidsif by enabeling all logs. Options: dependencies (set dependency logs to debug), all (set all logs to debug), yt-dlp (enable yt-dlp logs). Only affects the console logs, for also logging that on the logfile the config file has to be edited.",
        choices=["dependencies", "all", "yt-dlp"],
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="use vidsift <command> --help for more details about the commands",
    )

    init_parser = register_init(subparsers)
    run_parser = register_run(subparsers)
    config_parser = register_config(subparsers)
    process_parser = register_process(subparsers)
    videos_parser = register_videos(subparsers)
    schedule_parser = register_schedule(subparsers)
    service_parser = register_service(subparsers)
    log_parser = register_logs(subparsers)

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    if args.command == "logs" and args.follow and args.all_files:
        parser.error("--all-files cannot be used with --follow")

    if args.command == "process" and args.fake_download and args.download is False:
        parser.error("--fake-download can only be used with --download")

    return args
