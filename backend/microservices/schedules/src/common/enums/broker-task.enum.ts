export const BrokerTask = {
  SCHEDULE_SINGLE_JOB: 'jobs.schedule.single',
  SCHEDULE_CRON_JOB: 'jobs.schedule.cron',
  RESCHEDULE_SINGLE_JOB: 'jobs.reschedule.single',
  RESCHEDULE_CRON_JOB: 'jobs.reschedule.cron',
  UNSCHEDULE_SINGLE_JOB: 'jobs.unschedule.single',
  UNSCHEDULE_CRON_JOB: 'jobs.unschedule.cron',
} as const;
