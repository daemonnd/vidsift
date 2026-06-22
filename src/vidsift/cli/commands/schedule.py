from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.runtime.scheduler import BackgroundServiceManager


def register_schedule(subparsers):
    schedule_parser = subparsers.add_parser("schedule", help="Run the vidsift pipeline infinite, wait a certain amount of time between each run")
    schedule_parser.add_argument(
        "--sleep-interval",
        help="How many seconds vidsift should sleep between each run, default: 1800 (30min)",
        type=int
    )

    schedule_parser.set_defaults(func=handle_background_service)

    return schedule_parser


def handle_background_service(args, config):
    background_service_manager = BackgroundServiceManager(
        orchestrator=VidsiftOrchestrator(
            config=config
        ),
        config=config,
    )
    if args.sleep_interval:
        background_service_manager.run(
            sleep_interval=args.sleep_interval
        )
    background_service_manager.run()


