"""
Main file of vidsift

Tasks:
- parse CLI flags
- load config
- call one orchestrator (vidsift_pipeline.py)

"""
#import argparse

from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.shared.logging.config import configure_logging


class VidsiftCLI:
    def __init__(self) -> None:
        configure_logging()
#        self.config_parser: ConfigParser = ConfigParser()
        self.orchestrator: VidsiftOrchestrator = VidsiftOrchestrator(["UCo71RUe6DX4w-Vd47rFLXPg"])
    def start_pipeline(self) -> None:
        self.orchestrator.run()


if __name__ == "__main__":
    vidsift_app: VidsiftCLI = VidsiftCLI()
    vidsift_app.start_pipeline()
