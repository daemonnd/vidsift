from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.runtime.scheduler import BackgroundServiceManager


def register_schedule(subparsers):
    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Run the vidsift pipeline infinite, wait a certain amount of time between each run",
    )
    schedule_parser.add_argument(
        "--sleep-interval",
        help="How many seconds vidsift should sleep between each run, default: 1800 (30min)",
        type=int,
    )

    # args for skipping interrupted or new videos
    processing_exclusives = schedule_parser.add_mutually_exclusive_group()
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
    schedule_parser.set_defaults(func=handle_background_service)

    return schedule_parser


def handle_background_service(args, config, run_id):
    background_service_manager = BackgroundServiceManager(
        orchestrator=VidsiftOrchestrator(config=config),
        config=config,
        run_id=run_id,
    )
    if args.sleep_interval:
        background_service_manager.run(sleep_interval=args.sleep_interval)
    background_service_manager.run()
