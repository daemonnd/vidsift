from vidsift.features.initialization.init_vidsift import InitVidsift


def register_init(subparsers):
    run_parser = subparsers.add_parser("init", help="Initialize vidsift by creating necessary dirs and setting the default config")

    run_parser.set_defaults(func=handle_init)
    run_parser.add_argument(
        "--force",
        help="Overwrite config data",
        default=False,
        action="store_true"
    )


    return run_parser


def handle_init(args, config):
    vidsift_init: InitVidsift = InitVidsift(force=args.force)
    vidsift_init.initialize()
