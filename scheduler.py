import time
from .utils.metrics import observe_attempt
from .utils.stopwatch import Stopwatch
from .utils.logger import get_logger

logger = get_logger("shroud")

def run_scheduler(dry_run: bool = True):
    logger.info("Shroud scheduler starting... (dry_run=%s)", dry_run)
    sw = Stopwatch()

    try:
        while True:
            sw.start()
            logger.info("Checking queue...")

            # Placeholder job
            job = {"id": 1, "content": "Hello from Shroud"}

            if job:
                if dry_run:
                    logger.info("[Dry Run] Would dispatch job: %s", job["content"])
                else:
                    logger.info("Dispatching real job: %s", job["content"])
                observe_attempt(True)

            elapsed = sw.stop()
            logger.info("Cycle complete in %.2fs. Sleeping 5s...", elapsed)
            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")

if __name__ == "__main__":
    run_scheduler(dry_run=True)
