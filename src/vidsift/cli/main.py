from argparse import ArgumentParser

from vidsift.cli.commands.config import handle_config, register_config
from vidsift.cli.commands.process import register_process
from vidsift.cli.commands.run import handle_pipeline_run, register_run
from vidsift.cli.commands.schedule import register_schedule
from vidsift.cli.commands.videos import register_videos


def parse_args():
    parser = ArgumentParser(
        prog="vidsift",
        description="AI-powered YouTube feed filtering and transcript-based video validation and processing",
        suggest_on_error=True,
    )


    parser.add_argument("-V", "--version", 
                        help="Print version", 
                        action="version",
                        version="vidsift v0.0.1")
    parser.add_argument(
        "--config",
        help="Use custom config for this run",
        )
    parser.add_argument(
        "--loglevel", 
        help="Set the loglevel console logging for one run",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )
    parser.add_argument(
        "--global-ai-model",
        help="Set the AI model for all AI usages"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="use vidsift <command> --help for more details about the commands"
    )

    run_parser = register_run(subparsers)
    config_parser = register_config(subparsers)
    process_parser = register_process(subparsers)
    videos_parser = register_videos(subparsers)
    schedule_parser = register_schedule(subparsers)




    return parser.parse_args()
