import argparse
import os


def launch(args: any):
    # try:
    if args.command in ["server", "serve", "s"]:
        os.environ['APP'] = "server"
        from podcast.launcher.server import launch as server_launch
        server_launch(args.host, int(args.port), args.reload)
    elif args.command == "rq":
        os.environ['APP'] = f"rq_{args.name}"
        from podcast.launcher.server import launch as server_launch
        from podcast.launcher.rq import launch as rq_launch
        rq_launch(args.name)
    elif args.command == "scheduler":
        from podcast.launcher.server import launch as server_launch
        from podcast.launcher.scheduler import launch as scheduler_launch
        scheduler_launch()
    # except Exception as e:
    #     import podcast.pkg.client.log as logging
    #     logging.exception(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Anything to podcast.')
    subparsers = parser.add_subparsers(
        title='select argument from below:', dest='command')
    server = subparsers.add_parser(
        'server', aliases=['serve', 's'], help='launch server')
    server.add_argument('--host', required=False,
                        help='listen host, default as "127.0.0.1"')
    server.add_argument('--port', required=False,
                        help='listen port, default as "8576"')
    server.add_argument('--reload', action="store_true",
                        help='reload, default as "False"')

    server.set_defaults(host='0.0.0.0', port='8576', reload=False)

    rq = subparsers.add_parser('rq', help='launch rq')
    rq.add_argument('--name',
                    required=True,
                    help='select a queue such as ("zh", "en", "ja", "de", "nl", "fr", "es", "uk", "other")',
                    choices=["zh", "en", "ja", "de", "nl", "fr", "es", "uk", "other"])

    rq = subparsers.add_parser('scheduler', help='launch rq')

    parser_args = parser.parse_args()
    launch(parser_args)
