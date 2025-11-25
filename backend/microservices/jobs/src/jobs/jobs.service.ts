import { Injectable, Logger } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bullmq';
import { Job, Queue } from 'bullmq';
import { v4 as uuidv4 } from 'uuid';

import { loadConfig } from '@app/config';
import { ConfigService } from '@nestjs/config';
import {
  JobRescheduleCronDto,
  JobRescheduleSingleDto,
  JobScheduleCronDto,
  JobScheduleSingleDto,
  JobUnscheduleCronDto,
  JobUnscheduleSingleDto,
} from './dtos';
import { CronJob, SingleJob } from './entities';
import { JobType } from './enums';
import { JobPayload } from './types';
import { JobException } from './exceptions';

@Injectable()
export class JobsService {
  private readonly logger = new Logger(JobsService.name);
  private readonly config: unknown;

  constructor(
    @InjectQueue(loadConfig().broker.jobsQueueName)
    private readonly jobsQueue: Queue<Job<JobPayload>>,
    private readonly configService: ConfigService,
  ) {}

  async scheduleSingle(
    scheduleSingleDto: JobScheduleSingleDto,
  ): Promise<SingleJob> {
    const delay =
      new Date(scheduleSingleDto.executionDate).getTime() -
      new Date().getTime();
    const id = uuidv4();
    try {
      const job = await this.jobsQueue.add(
        scheduleSingleDto.name,
        {
          ...scheduleSingleDto.payload,
          ackEventName: scheduleSingleDto.ackEventName,
        },
        {
          delay,
          jobId: id,
        },
      );

      this.logger.debug(
        `Added single job ${job.name} with id = ${job.id} to the queue`,
        scheduleSingleDto.payload,
      );

      return {
        executionDate: scheduleSingleDto.executionDate,
        id: job.id || 'no-id',
        name: job.name,
        type: JobType.SINGLE,
      };
    } catch (err) {
      throw new JobException('error while scheduling single job', err, id);
    }
  }

  async scheduleCron(scheduleCronDto: JobScheduleCronDto): Promise<CronJob> {
    const scheudulerId = uuidv4();

    try {
      const job = await this.jobsQueue.upsertJobScheduler(
        scheudulerId,
        {
          pattern: scheduleCronDto.cron,
        },
        {
          name: scheduleCronDto.name,
          data: {
            ...scheduleCronDto.payload,
            ackEventName: scheduleCronDto.ackEventName,
          },
        },
      );

      this.logger.debug(
        `Added cron job ${job.name} with id = ${job.id} to the queue`,
        scheduleCronDto.payload,
      );

      return {
        type: JobType.CRON,
        cron: scheduleCronDto.cron,
        id: scheudulerId,
        name: job.name,
      };
    } catch (err) {
      throw new JobException(
        'error while scheduling cron job',
        err,
        scheudulerId,
      );
    }
  }

  async rescheduleSingle(
    rescheduleSingleDto: JobRescheduleSingleDto,
  ): Promise<SingleJob> {
    try {
      const job = await this.jobsQueue.getJob(rescheduleSingleDto.id);

      if (!job) {
        throw new Error(
          'Cannot reschedule single job, because it does not exist',
        );
      }

      const newDelay =
        new Date(rescheduleSingleDto.executionDate).getTime() -
        new Date().getTime();

      if (newDelay <= 0) {
        throw new Error('Cannot reschedule single job with date in the past');
      }

      await job.remove();
      await this.jobsQueue.add(job.name, job.data, {
        ...job.opts,
        delay: newDelay,
      });

      this.logger.debug(
        `Rescheduled single job ${job.name} with id = ${job.id} to ${rescheduleSingleDto.executionDate}`,
      );

      return {
        type: JobType.SINGLE,
        executionDate: rescheduleSingleDto.executionDate,
        id: job.id || 'no-id',
        name: job.name,
      };
    } catch (err) {
      throw new JobException(
        'error while rescheduling single job',
        err,
        rescheduleSingleDto.id,
      );
    }
  }

  async rescheduleCron(
    rescheduleCronDto: JobRescheduleCronDto,
  ): Promise<CronJob> {
    try {
      const jobScheduler = await this.jobsQueue.getJobScheduler(
        rescheduleCronDto.id,
      );

      this.logger.debug(jobScheduler);

      if (!jobScheduler) {
        throw new Error(
          `Cannot reschedule cron job with id ${rescheduleCronDto.id}, because it does not exist`,
        );
      }

      await this.jobsQueue.upsertJobScheduler(
        jobScheduler.key,
        {
          pattern: rescheduleCronDto.cron,
        },
        {
          data: jobScheduler.template?.data,
          name: jobScheduler.name,
          opts: jobScheduler.template?.opts,
        },
      );

      this.logger.debug(
        `Rescheduled cron job ${jobScheduler.name} with id = ${jobScheduler.key} to ${rescheduleCronDto.cron}`,
      );

      return {
        type: JobType.CRON,
        cron: rescheduleCronDto.cron,
        id: jobScheduler.key,
        name: jobScheduler.name,
      };
    } catch (err) {
      throw new JobException(
        'error while rescheduling cron job',
        err,
        rescheduleCronDto.id,
      );
    }
  }

  async unscheduleSingle(
    unscheduleSingleDto: JobUnscheduleSingleDto,
  ): Promise<SingleJob> {
    // TODO: check if job is single job

    try {
      const job = await this.jobsQueue.getJob(unscheduleSingleDto.id);

      if (!job) {
        throw new Error(
          'Cannot reschedule single job, because it does not exist',
        );
      }

      await job.remove();

      this.logger.debug(
        `Unscheduled single job ${job.name} with id = ${job.id}`,
      );

      return {
        type: JobType.SINGLE,
        id: job.id || 'no-id',
        name: job.name,
        executionDate: new Date(
          job.timestamp + (job.opts.delay || 0),
        ).toISOString(),
      };
    } catch (err) {
      throw new JobException(
        'error while unscheduling single job',
        err,
        unscheduleSingleDto.id,
      );
    }
  }

  async unscheduleCron(
    unscheduleCronDto: JobUnscheduleCronDto,
  ): Promise<CronJob> {
    try {
      const jobScheduler = await this.jobsQueue.getJobScheduler(
        unscheduleCronDto.id,
      );

      if (!jobScheduler) {
        throw new Error(
          'Cannot unschedule cron job, because it does not exist',
        );
      }

      await this.jobsQueue.removeJobScheduler(jobScheduler.key);

      this.logger.debug(
        `Unscheduled cron job ${jobScheduler.name} with id = ${jobScheduler.key}`,
      );

      return {
        type: JobType.CRON,
        cron: jobScheduler.pattern || 'no-pattern',
        id: jobScheduler.key,
        name: jobScheduler.name,
      };
    } catch (err) {
      throw new JobException(
        'error while unscheduling cron job',
        err,
        unscheduleCronDto.id,
      );
    }
  }
}
