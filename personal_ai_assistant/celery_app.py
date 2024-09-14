from celery import Celery
from celery.schedules import crontab
from personal_ai_assistant.config import settings

app = Celery('personal_ai_assistant',
             broker=settings.redis_url.get_secret_value(),
             backend=settings.redis_url.get_secret_value(),
             include=['personal_ai_assistant.tasks'])

app.conf.update(
    result_expires=3600,
)

app.conf.beat_schedule = {
    'check-emails-every-5-minutes': {
        'task': 'personal_ai_assistant.tasks.check_and_process_new_emails',
        'schedule': 300.0,
    },
    'sync-calendar-daily': {
        'task': 'personal_ai_assistant.tasks.sync_calendar_events',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
    'clean-up-old-data-weekly': {
        'task': 'personal_ai_assistant.tasks.clean_up_old_data',
        'schedule': crontab(day_of_week=0, hour=1, minute=0),  # Run weekly on Sunday at 1 AM
    },
    'update-task-statuses-hourly': {
        'task': 'personal_ai_assistant.tasks.update_task_statuses',
        'schedule': crontab(minute=0),  # Run every hour
    },
    'generate-daily-summary': {
        'task': 'personal_ai_assistant.tasks.generate_daily_summary',
        'schedule': crontab(hour=23, minute=55),  # Run daily at 23:55
    },
}

if __name__ == '__main__':
    app.start()
