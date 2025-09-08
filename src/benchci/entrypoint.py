import benchci
import argparse


def run_evaluation(config_file_path):
    benchci.evaluation.run_evaluation(config_file_path)


def build_pages(): ...


def build_charts(): ...


def main():
    parser = argparse.ArgumentParser(description="BenchCI Command Line Interface")
    subparsers = parser.add_subparsers(dest="command")

    eval_parser = subparsers.add_parser("evaluate", help="Run evaluations")
    eval_parser.set_defaults(func=run_evaluation)
    # TODO: Should we set this to the top level `parser`?
    eval_parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the YAML configuration file",
    )

    page_parser = subparsers.add_parser("build-pages", help="Build HTML pages")
    page_parser.set_defaults(func=build_pages)
    page_parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the YAML configuration file",
    )

    chart_parser = subparsers.add_parser("build-charts", help="Build charts")
    chart_parser.set_defaults(func=build_charts)
    chart_parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the YAML configuration file",
    )

    args = parser.parse_args()

    config_file_path = args.config if hasattr(args, "config") else "config.yaml"

    if hasattr(args, "func"):
        args.func(config_file_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
