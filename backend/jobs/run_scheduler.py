"""Download forecasts and re-score every site right away, then every 6 hours, until you press Ctrl+C.

Run from the backend folder:  python -m jobs.run_scheduler
(When the app is deployed, Render's scheduled job feature will run these instead.)
"""
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from jobs import download_forecasts, score_nights


def update_all():
    """New forecasts first, then new scores based on them."""
    download_forecasts.run()
    score_nights.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scheduler = BlockingScheduler()
    scheduler.add_job(update_all, "interval", hours=6, next_run_time=datetime.now(), id="update_all")
    logging.info("Scheduler started: updating forecasts and scores now and every 6 hours. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
