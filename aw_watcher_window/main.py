import logging
import traceback
import sys
import os
from time import sleep
from datetime import datetime, timezone

from aw_core.models import Event
from aw_core.log import setup_logging
from aw_client import ActivityWatchClient

from .lib import get_current_window
from .config import parse_args
from .macos_permissions import background_ensure_permissions


logger = logging.getLogger(__name__)

# run with LOG_LEVEL=DEBUG
log_level = os.environ.get("LOG_LEVEL")
if log_level:
    logger.setLevel(logging.__getattribute__(log_level.upper()))


def main():
    args = parse_args()

    if sys.platform.startswith("linux") and (
        "DISPLAY" not in os.environ or not os.environ["DISPLAY"]
    ):
        raise Exception("DISPLAY environment variable not set")

    setup_logging(
        name="aw-watcher-window",
        testing=args.testing,
        verbose=args.verbose,
        log_stderr=True,
        log_file=True,
    )

    if sys.platform == "darwin":
        background_ensure_permissions()

    client = ActivityWatchClient("aw-watcher-window", testing=args.testing)

    bucket_id = "{}_{}".format(client.client_name, client.client_hostname)
    event_type = "currentwindow"

    client.create_bucket(bucket_id, event_type, queued=True)

    logger.info("aw-watcher-window started")

    sleep(1)  # wait for server to start
    with client:
        heartbeat_loop(
            client,
            bucket_id,
            poll_time=args.poll_time,
            strategy=args.strategy,
            exclude_title=args.exclude_title,
        )


def heartbeat_loop(client, bucket_id, poll_time, strategy, exclude_title=False):
    while True:
        if os.getppid() == 1:
            logger.info("window-watcher stopped because parent process died")
            break

        try:
            current_window = get_current_window(strategy)
            logger.debug(current_window)
        except Exception as e:
            logger.error(
                "Exception thrown while trying to get active window: {}".format(e)
            )
            traceback.print_exc()
            current_window = {
                "app": "unknown",
                "title": "unknown",
                "id": "unknown",
                "pid": "unknown",
                "user": "unknown",
                "description": "unknown",
                "executable": "unknown",
                "commandLine": "unknown"
            }

        now = datetime.now(timezone.utc)
        if current_window is None:
            logger.debug("Unable to fetch window, trying again on next poll")
        else:
            if exclude_title:
                current_window["title"] = "excluded"

            current_window_event = Event(timestamp=now, data=current_window)

            # Set pulsetime to 1 second more than the poll_time
            # This since the loop takes more time than poll_time
            # due to sleep(poll_time).
            client.heartbeat(
                bucket_id, current_window_event, pulsetime=poll_time + 1.0, queued=True
            )

        sleep(poll_time)
