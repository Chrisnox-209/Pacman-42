import argparse
from typing import Any


class ConfigPathError(Exception):
    """
    Exception raised for errors related to output file paths.
    """
    pass


def check_argument() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args: argparse.Namespace = parser.parse_args()
    return args.config
