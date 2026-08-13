import argcomplete

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
    run_parser.add_argument( 
        "--fake-download",
        nargs='?',
        const=True,  # value when flag is used WITHOUT an argument
        default=None,  # value when flag is NOT used at all
        help="""Simulate the download of videos without actually downloading them.
        Instead, the url of the video to the filepath specified in the config file, 
        to override that config file value, use
        --fake-download-path /path/to/fake/download/file.
        The default value for that is the download targed dir / 'to_watch.md'.
        Only applies to videos that get ether downloaded with the action 'download' or through the validation result 'download'""",
    ).completer = argcomplete.completers.FilesCompleter
    run_parser.set_defaults(func=handle_pipeline_run)

    return run_parser


def handle_pipeline_run(args, config, run_id):
    run_manager = RunManager(run_id)
    run_manager.start_run(run_type="manual_pipeline_run")

    try:
        orchestrator = VidsiftOrchestrator(config=config)
        orchestrator.run()
    finally:
        run_manager.end_run()
