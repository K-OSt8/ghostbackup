# cli.py
import argparse
import datetime
import logging
import sys

from pathlib import Path
from . import LOGGER_NAME
from .config import loadConfig
from .backup import BackUp

def main():

    parser = argparse.ArgumentParser(description="Ghost Back-up")
    parser.add_argument("-f", "--force", action="store_true", help="Backup in any case: Skip check if archive is up-to-date")
    parser.add_argument("-c", "--config", type=Path, help="Path to configuration default to '~/.ghost-backup.cfg'")
    parser.add_argument("-v", "--verbose", action="store_true", help="activate verbose output")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        handlers={logging.StreamHandler(sys.stderr)},
                        level=logging.DEBUG if args.verbose else logging.INFO)
    log = logging.getLogger(LOGGER_NAME)
    start = datetime.datetime.now()
    log.info("Start backup-program")
    try:
        if args.verbose and args.force:
            log.info("Force mode set: Skip up-to-date-check")
        backup = BackUp(loadConfig(cfg_path=args.config))
        backup.backup(force=args.force)
    except Exception as e:
        log.error(f"Could not back-up: {e}", exc_info=log.getEffectiveLevel()==logging.DEBUG)
        return 1
    log.info("Terminated backup-program after %.2f sec.", datetime.datetime.now().timestamp() - start.timestamp())
    return 0