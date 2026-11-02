"""Run the forecast download right away, then every 6 hours, until you press Ctrl+C.

Run from the backend folder:  python -m jobs.run_scheduler
(When the app is deployed, Render's scheduled job feature will run download_forecasts instead.)
"""
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from jobs.download_forecasts import run

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scheduler = BlockingScheduler()
    scheduler.add_job(run, "interval", hours=6, next_run_time=datetime.now(), id="download_forecasts")
    logging.info("Scheduler started: downloading forecasts now and every 6 hours. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
