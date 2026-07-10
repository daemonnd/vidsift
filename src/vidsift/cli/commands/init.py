

def register_init(subparsers):
    run_parser = subparsers.add_parser("init", help="Initialize vidsift by creating necessary dirs and setting the default config")

    run_parser.set_defaults()
    run_parser.add_argument(
        "--force",
        help="Overwrite any config data that already exists",
        default=False,
        action="store_true"
    )


    return run_parser

# gets called directly by main
