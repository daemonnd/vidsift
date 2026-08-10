from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.shared.run_manager import RunManager


def register_run(subparsers):
    run_parser = subparsers.add_parser("run", help="Run the vidsift pipeline")

    # args for skipping interrupted or new videos
    processing_exclusives = run_parser.add_mutually_exclusive_group()
    processing_exclusives.add_argument(
        "--skip-interrupted",
        help="Only process new videos, skips interrupted ones",
        action="store_true",
    )

    processing_exclusives.add_argument(
        "--skip-new",
        help="Only process interrupted videos, skip the new ones.",
        action="store_true",
    )
    run_parser.set_defaults(func=handle_pipeline_run)

    return run_parser


def handle_pipeline_run(args, config):
    run_manager = RunManager()
    run_manager.start_run(run_type="manual_pipeline_run")

    try:
        orchestrator = VidsiftOrchestrator(config=config)
        orchestrator.run()
    finally:
        run_manager.end_run()
