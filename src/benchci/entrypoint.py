import benchci
import argparse


def main():
    parser = argparse.ArgumentParser(description="BenchCI Command Line Interface")

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the YAML configuration file",
    )

    subparsers = parser.add_subparsers(dest="command")

    eval_parser = subparsers.add_parser("evaluate", help="Run evaluations")
    eval_parser.set_defaults(func=benchci.evaluation.run_evaluation)

    page_parser = subparsers.add_parser("build-pages", help="Build HTML pages")
    page_parser.set_defaults(func=benchci.pages.build_pages)

    chart_parser = subparsers.add_parser("build-charts", help="Build charts")
    chart_parser.set_defaults(func=benchci.charts.build_charts)

    compat_parser = subparsers.add_parser("compat", help="Compat logs")
    compat_parser.set_defaults(func=benchci.compat.compat_logs)

    server_parser = subparsers.add_parser("serve", help="Serve reports")
    server_parser.set_defaults(func=benchci.server.start_server)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args.config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
