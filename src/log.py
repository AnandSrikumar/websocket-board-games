import logging
import logging.handlers
import queue
import sys

_LOG_QUEUE = queue.Queue(-1)

_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(threadName)s | %(name)s | %(message)s"
)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)

_queue_handler = logging.handlers.QueueHandler(_LOG_QUEUE)

_listener = logging.handlers.QueueListener(
    _LOG_QUEUE,
    _console_handler,
    respect_handler_level=True,
)

_listener_started = False


def setup_logging(level: int = logging.INFO) -> None:
    global _listener_started

    if _listener_started:
        return

    root_logger = logging.getLogger()

    root_logger.setLevel(level)
    root_logger.addHandler(_queue_handler)

    _listener.start()
    _listener_started = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def shutdown_logging() -> None:
    global _listener_started

    if not _listener_started:
        return

    _listener.stop()
    _listener_started = False
