#!/usr/bin/env python3
import sys
from storage.db import init_db


def main():
    init_db()
    from ui.cli_app import cli
    cli()


if __name__ == "__main__":
    main()
