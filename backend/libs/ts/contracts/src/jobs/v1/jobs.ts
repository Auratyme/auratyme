import { Observable } from 'rxjs';

export enum JobType {
  SINGLE = 0,
  CRON = 1,
}

export type SingleJob = {
  id: string;
  name: string;
  executionDate: string;
  type: JobType;
};
export type CronJob = {
  id: string;
  name: string;
  cron: string;
  type: JobType;
};

export type JobScheduleSingleRequest = {
  name: string;
  executionDate: string;
  ackEventName: string;
  payload: Record<string, string>;
};
export type JobScheduleCronRequest = {
  name: string;
  cron: string;
  ackEventName: string;
  payload: Record<string, string>;
};

export type JobRescheduleSingleRequest = {
  id: string;
  executionDate: string;
};
export type JobRescheduleCronRequest = {
  id: string;
  cron: string;
};

export type JobUnscheduleSingleRequest = {
  id: string;
};
export type JobUnscheduleCronRequest = {
  id: string;
};

export interface JobsService {
  scheduleSingle(payload: JobScheduleSingleRequest): Observable<SingleJob>;
  scheduleCron(payload: JobScheduleCronRequest): Observable<CronJob>;

  rescheduleSingle(payload: JobRescheduleSingleRequest): Observable<SingleJob>;
  rescheduleCron(payload: JobRescheduleCronRequest): Observable<CronJob>;

  unscheduleSingle(payload: JobUnscheduleSingleRequest): Observable<SingleJob>;
  unscheduleCron(payload: JobUnscheduleCronRequest): Observable<CronJob>;
}

export enum JobsConfig {
  URL = 'jobs:5000',
  PACKAGE = 'job',
  PROTO_PATH = '/libs/proto/jobs/v1/jobs.proto',
  SERVICE_NAME = 'JobsService',
  SCHEDULE_SINGLE_METHOD = 'ScheduleSingle',
  SCHEDULE_CRON_METHOD = 'ScheduleCron',
  RESCHEDULE_SINGLE_METHOD = 'RescheduleSingle',
  RESCHEDULE_CRON_METHOD = 'RescheduleCron',
  UNSCHEDULE_SINGLE_METHOD = 'UnscheduleSingle',
  UNSCHEDULE_CRON_METHOD = 'UnscheduleCron',
}
