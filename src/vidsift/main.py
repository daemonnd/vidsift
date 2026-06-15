"""
Main file of vidsift

Tasks:
- parse CLI flags
- load config
- call one orchestrator (vidsift_pipeline.py)

"""
import argparse
import logging
from pathlib import Path

from rich import print
from rich.console import Console

from vidsift.config.errors import (ConfigError, ConfigFileNotFoundError,
                                   ConfigFilePermissionError,
                                   ConfigValidationError, InvalidConfigError)
from vidsift.config.loader import load_config
from vidsift.config.models import AppConfig
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.shared.logging.bootstrap_logger import setup_bootstrap_logging
from vidsift.shared.logging.config import configure_logging


class VidsiftCLI:
    def __init__(self) -> None:
        """
        Manages vidsift bootstraping flow:
        1. setup bootstrap logging
        2. parse CLI flags
        3. load config.toml
        4. apply CLI overrides
        5. validate final config
        6. configure logging
        7. build application
        8. execute command
        """
        # setup bootstrap logging
        setup_bootstrap_logging()
        logger = logging.getLogger(__name__)

        # parse CLI flags
        args = self.parse_args()

        # load config.toml


        try:
            # load config.toml
            config = load_config()
        except InvalidConfigError as e:
            logger.exception(f"InvalidConfigError: {str(e)}")
            exit(1)
        except ConfigFileNotFoundError as e:
            logger.exception(f"ConfigFileNotFoundError: {str(e)}")
            exit(1)
        except ConfigFilePermissionError as e:
            logger.exception(f"ConfigFilePermissionError: {str(e)}")
            exit(1)
        except ConfigValidationError as e:
            logger.exception(f"ConfigValidationError: {str(e)}")
            exit(1)
        except ConfigError as e:
            logger.exception(f"ConfigError: {str(e)}")
            exit(1)

        updates = {}
 
        if args.loglevel is not None:
            updates["level"] = args.loglevel

        config = config.model_copy(update=updates)
        self.config: AppConfig = config
 


        configure_logging(self.config)  # configure logger after app and logger config is loaded


        # execute command
        if hasattr(args, "func"):
            args.func(args)


    def handle_pipeline_run(self, args):
        channel_id_list = ["UCo71RUe6DX4w-Vd47rFLXPg", ]

        self.orchestrator = VidsiftOrchestrator(channel_id_list, config=self.config)

        self.orchestrator.run()

    def handle_config_show(self, args):
        CONFIG_FILE_PATH: Path = Path(Path.home() / ".config" / "vidsift" / "config.toml")
        print(f"Config file: {CONFIG_FILE_PATH}\n")
        with open(file=CONFIG_FILE_PATH, mode="r") as f:
            print(f.read())



    def handle_videos_list(self, args):
        repo = VideoProcessingRepository()
        try:
            if args.status:
                videos = repo.get_by_status(args.status)
            else:
                videos = repo.get_all()

            console = Console()

            for video in videos:
                console.print(video)
        finally:
            repo.close()

    def handle_videos_set_status(self, args):
        repo = VideoProcessingRepository()
        try:
            if args.video_id and args.status:
                repo.set_status(args.video_id, args.status)
        finally:
            repo.close()

    #    def run(self):

            #if args.version:
            #print("VERSION")
            #elif args.command == "run":
            #print("RUN")
            #self.orchestrator.run()
            #elif args.command == "config":
            #print("CONFIG")
            #exit(0)
            #elif args.command == "process":
            #print("PROCESS")
            #exit(0)



#        self.config_parser: ConfigParser = ConfigParser()


    def parse_args(self):
        parser = argparse.ArgumentParser(
            prog="vidsift",
            description="AI-powered YouTube feed filtering and transcript-based video validation and processing",
            suggest_on_error=True,
        )

        parser.add_argument("-V", "--version", 
                            help="Print version", 
                            action="version",
                            version="vidsift v0.0.1")
 
        subparsers = parser.add_subparsers(
            dest="command",
            required=True,
            help="use vidsift <command> --help for more details about the commands"
        )

 
        run_parser = subparsers.add_parser("run", help="Run the vidsift pipeline")
        run_parser.add_argument("--loglevel", help="Set the loglevel for file and console for one run")


        process_parser = subparsers.add_parser("process", help="Process a certain URL")
        process_parser.add_argument("--url", help="Process a specific video")


        config_parser = subparsers.add_parser("config", help="Edit or show the vidsift config")
        config_subparsers = config_parser.add_subparsers(dest="config_command")
        show_parser = config_subparsers.add_parser("show", help="Show config path")

        videos_parser = subparsers.add_parser("videos", help="Edit view or video processed videos")
        videos_subparsers = videos_parser.add_subparsers(dest="videos_command")
        video_list = videos_subparsers.add_parser("list", help="list already processed videos")
        video_list.add_argument(
            "-s", "--status", 
            help="filter by processing status ('downloading', 'summarizing', 'done', 'failed', 'validating'",
            choices=["downloading", "summarizing", "done", "failed", "validating"]
        )

        video_set_status = videos_subparsers.add_parser(
            "set-status",
            help="Set the status of <video id> to <status>",
        )
        video_set_status.add_argument(
            "--video-id",
            help="ID of the target video"
        )
        video_set_status.add_argument(
            "--status",
            help="Target status of video",
            choices=["downloading", "summarizing", "done", "failed", "validating"]
        )




        run_parser.set_defaults(func=self.handle_pipeline_run)
        show_parser.set_defaults(func=self.handle_config_show)
        video_set_status.set_defaults(func=self.handle_videos_set_status)
        video_list.set_defaults(func=self.handle_videos_list)

        return parser.parse_args()



if __name__ == "__main__":
    vidsift_app: VidsiftCLI = VidsiftCLI()
    #vidsift_app.run()
