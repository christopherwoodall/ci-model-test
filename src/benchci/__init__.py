# ruff: noqa
# fmt: off
# Configure clean imports for the package
# See: https://hynek.me/articles/testing-packaging/


from . import compat, evaluation, reports, server

from .compat import compat_logs
from .evaluation import run_evaluation
from .server import start_server

from .reports import charts, pages, spider
from .reports.pages import build_pages
from .reports.charts import build_charts
from .reports.spider import build_spider_chart


__all__ = [
    "compat",
        "compat_logs",

    "charts",
        "build_charts",

    "evaluation",
        "run_evaluation",
    
    "pages",
        "build_pages",

    "reports",
        "spider",
            "build_spider_chart",
        "server",
            "start_server",
        "pages",
            "build_pages",
        "charts",
            "build_charts",
]
