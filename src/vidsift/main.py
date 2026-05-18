"""
Main file of vidsift

Tasks:
- parse CLI flags
- load config
- call one orchestrator (vidsift_pipeline.py)

"""
import argparse

from vidsift.config.parser import ConfigParser
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator


class VidsiftCLI:
    def __init__(self) -> None:
        self.config_parser: ConfigParser = ConfigParser()
        self.orchestrator: VidsiftOrchestrator = VidsiftOrchestrator()
    def start_pipeline(self) -> None:
