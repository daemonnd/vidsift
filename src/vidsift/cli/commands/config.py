from pathlib import Path

from rich.console import Console


def handle_config_show(self, args):
    if args.file:
        CONFIG_FILE_PATH: Path = Path(Path.home() / ".config" / "vidsift" / "config.toml")
        if args.config:
            CONFIG_FILE_PATH = args.config
        print(f"Config file: {CONFIG_FILE_PATH}\n")
        with open(file=CONFIG_FILE_PATH, mode="r") as f:
            print(f.read())

    elif args.filepath:
        CONFIG_FILE_PATH: Path = Path(Path.home() / ".config" / "vidsift" / "config.toml")
        if args.config:
            CONFIG_FILE_PATH = args.config
        print(f"Config file: {CONFIG_FILE_PATH}")


    else:
        console = Console()

        console.print(self.config)

