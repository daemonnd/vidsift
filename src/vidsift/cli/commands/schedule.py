from argparse import ArgumentParser

from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator


def register_run(subparsers):
    run_parser = subparsers.add_parser("run", help="Run the vidsift pipeline")

    run_parser.set_defaults(func=handle_pipeline_run)

    return run_parser


def handle_pipeline_run(args, config):
    channel_id_list = ["UCo71RUe6DX4w-Vd47rFLXPg", ]

    orchestrator = VidsiftOrchestrator(channel_id_list, config=config)

    orchestrator.run()
