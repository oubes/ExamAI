# ---- Imports ---- #
import logging
import sys


# ---- Colors ---- #
class Colors:
    RESET = "\033[0m"
    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"


LEVEL_COLORS = {
    "DEBUG": Colors.BLUE,
    "INFO": Colors.GREEN,
    "WARNING": Colors.YELLOW,
    "ERROR": Colors.RED,
    "CRITICAL": Colors.MAGENTA,
}


# ---- Colored Formatter ---- #
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_COLORS.get(record.levelname, Colors.RESET)

        original_levelname = record.levelname
        original_name = record.name

        record.levelname = (
            f"{color}{record.levelname}{Colors.RESET}"
        )

        record.name = (
            f"{Colors.BLUE}{record.name}{Colors.RESET}"
        )

        formatted = super().format(record)

        # restore original values
        record.levelname = original_levelname
        record.name = original_name

        return formatted


# ---- Logging configuration ---- #
def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(asctime)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log"),
        ]
    )

    # ---- Apply Colors ---- #
    logging.getLogger().handlers[0].setFormatter(
        ColoredFormatter(
            "%(levelname)s: %(asctime)s - %(name)s - %(message)s"
        )
    )

    # ---- Prevent Overwriting Logs ---- #
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True