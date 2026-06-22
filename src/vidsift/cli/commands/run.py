from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.shared.run_manager import RunManager


def register_run(subparsers):
    run_parser = subparsers.add_parser("run", help="Run the vidsift pipeline")

    run_parser.set_defaults(func=handle_pipeline_run)

    return run_parser


def handle_pipeline_run(args, config):
    run_manager = RunManager()
    run_manager.start_run(owner="manual", run_type="manual_pipeline_run")

    try:
        orchestrator = VidsiftOrchestrator(config=config)
        orchestrator.run()
    finally:
        run_manager.end_run()
