# dependencies check
import logging
import subprocess
import sys

LOG = logging.getLogger("depcheck")
LOG.setLevel(logging.INFO)
file_handler = logging.FileHandler("depcheck.log")
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
LOG.addHandler(file_handler)
LOG.addHandler(console_handler)


def check():
    try:
        if sys.platform == "win32":
            subprocess.check_call(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            LOG.info("ffmpeg is installed.")
        elif sys.platform == "linux":
            subprocess.check_call(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            LOG.info("ffmpeg is installed.")
    except (OSError, IOError):
        LOG.error("ffmpeg is not installed.")
        sys.exit(1)
