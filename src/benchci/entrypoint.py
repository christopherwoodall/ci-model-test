import benchci
import argparse


def run_evaluation(config_file_path):
    benchci.evaluation.run_evaluation(config_file_path)


def build_pages(config_file_path):
    benchci.pages.build_pages(config_file_path)


def build_charts(config_file_path):
    benchci.charts.build_charts(config_file_path)


def compat_logs(config_file_path):
    benchci.compat.compat_logs(config_file_path)


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
    eval_parser.set_defaults(func=run_evaluation)

    page_parser = subparsers.add_parser("build-pages", help="Build HTML pages")
    page_parser.set_defaults(func=build_pages)

    chart_parser = subparsers.add_parser("build-charts", help="Build charts")
    chart_parser.set_defaults(func=build_charts)

    compat_parser = subparsers.add_parser("compat", help="Compat logs")
    compat_parser.set_defaults(func=compat_logs)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args.config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
