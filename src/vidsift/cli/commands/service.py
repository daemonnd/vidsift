import logging

from vidsift.services.bg_runner_service import BgRunnserService

logger = logging.getLogger(__name__)


def register_service(subparsers):
    schedule_parser = subparsers.add_parser(
        "service",
        help="Manage the OS vidsift background service that starts vidsift schedule once after boot",
    )
    exclusive_schedule_parser_group = schedule_parser.add_mutually_exclusive_group()
    exclusive_schedule_parser_group.add_argument(
        "--enable",
        help="Enable the background service for Linux, Windows or MacOS",
        action="store_true",
    )
    exclusive_schedule_parser_group.add_argument(
        "--disable",
        help="Disable the background service for Linux, Windows or MacOS",
        action="store_true",
    )
    exclusive_schedule_parser_group.add_argument(
        "--start",
        help="Start the service now",
        action="store_true",
    )
    exclusive_schedule_parser_group.add_argument(
        "--stop",
        help="Stop the service now",
        action="store_true",
    )
    exclusive_schedule_parser_group.add_argument(
        "--restart", help="Restart the service", action="store_true"
    )
    exclusive_schedule_parser_group.add_argument(
        "--status", help="Show the status of the service", action="store_true"
    )

    schedule_parser.set_defaults(func=handle_background_service)

    return schedule_parser


def handle_background_service(args, config, run_id):
    try:
        bg_runner_service = BgRunnserService()
        if args.enable:
            bg_runner_service.install_service()
        elif args.disable:
            bg_runner_service.uninstall_service()
        elif args.start:
            bg_runner_service.start_service()
        elif args.stop:
            bg_runner_service.stop_service()
        elif args.restart:
            bg_runner_service.restart_service()
        elif args.status:
            bg_runner_service.get_status()
        else:
            bg_runner_service.get_status()
    except Exception as e:
        logger.exception(f"{type(e).__name__}: {str(e)}")
