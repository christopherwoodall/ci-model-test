import argparse


def run_evaluation():
    ...


def build_pages():
    ...


def build_charts():
    ...


def main():
    parser = argparse.ArgumentParser(description="BenchCI Command Line Interface")
    subparsers = parser.add_subparsers(dest="command")

    eval_parser = subparsers.add_parser("evaluate", help="Run evaluations")
    eval_parser.set_defaults(func=run_evaluation)

    page_parser = subparsers.add_parser("build-pages", help="Build HTML pages")
    page_parser.set_defaults(func=build_pages)

    chart_parser = subparsers.add_parser("build-charts", help="Build charts")
    chart_parser.set_defaults(func=build_charts)
    
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func()
    else:
        parser.print_help()
    

if __name__ == "__main__":
    main()
