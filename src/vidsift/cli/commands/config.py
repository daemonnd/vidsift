from pathlib import Path

from platformdirs import user_config_dir
from rich.console import Console


def register_config(subparsers):
    config_parser = subparsers.add_parser("config", help="Edit or show the vidsift config")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)
    show_parser = config_subparsers.add_parser("show", help="Show config path")
    exclusive_show_parser_group = show_parser.add_mutually_exclusive_group()
    exclusive_show_parser_group.add_argument(
        "--file",
        help="Show contents of config file instead of current loaded config",
        action="store_true"
    )
    exclusive_show_parser_group.add_argument(
        "--filepath",
        help="Only show the file path of the current config file instead of the loaded config",
        action="store_true"
    )

    config_parser.set_defaults(func=handle_config)

    return config_parser

def handle_config(args, config):
    if args.file:
        CONFIG_FILE_PATH: Path = (Path(user_config_dir("vidsift")) / "config.toml")
        if args.config:
            CONFIG_FILE_PATH = args.config
        print(f"Config file: {CONFIG_FILE_PATH}\n")
        with open(file=CONFIG_FILE_PATH, mode="r") as f:
            print(f.read())

    elif args.filepath:
        CONFIG_FILE_PATH: Path = (Path(user_config_dir("vidsift")) / "config.toml")
        if args.config:
            CONFIG_FILE_PATH = args.config
        print(f"Config file: {CONFIG_FILE_PATH}")


    else:
        console = Console()

        console.print(config)

