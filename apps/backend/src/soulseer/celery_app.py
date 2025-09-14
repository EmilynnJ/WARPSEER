from celery import Celery
from .config import settings

celery = Celery(
    'soulseer',
    broker=settings.redis_url,
    backend=settings.redis_url
)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily payouts at 2am UTC
    sender.add_periodic_task(24*60*60, run_daily_payouts.s(), name='daily_payouts')

@celery.task
def run_daily_payouts():
    # TODO: Implement Stripe Connect transfers to readers with balance > $15
    return True