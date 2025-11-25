import { Inject, Injectable, Logger, OnModuleInit } from '@nestjs/common';

import { Dictionary } from 'common';
import { ClientGrpc } from '@nestjs/microservices';
import { firstValueFrom } from 'rxjs';
import { JobsRepository } from './jobs.repository';
import { ConfigService } from '@nestjs/config';
import { Config } from '../common/types';
import { DiToken } from '../common/enums';
import {
  JobsService as ClientJobsService,
  JobRescheduleCronRequest,
  JobRescheduleSingleRequest,
  JobScheduleCronRequest,
  JobScheduleSingleRequest,
  JobUnscheduleCronRequest,
  JobUnscheduleSingleRequest,
  SingleJob,
  CronJob,
} from 'contracts';
import { DbJob } from './types';
import { JobType } from './enums';

@Injectable()
export class JobsService<PayloadType extends Dictionary = Dictionary>
  implements OnModuleInit
{
  private clientJobsService: ClientJobsService;
  private readonly logger = new Logger(JobsService.name);
  private readonly jobsClientConfig: Config['jobsClient'];

  constructor(
    @Inject(DiToken.JOB_CLIENT) private client: ClientGrpc,
    private readonly jobsRepository: JobsRepository,
    readonly configService: ConfigService,
  ) {
    this.jobsClientConfig = configService.get<Config['jobsClient']>(
      'jobsClient',
    ) as Config['jobsClient'];
  }

  onModuleInit() {
    this.clientJobsService =
      this.client.getService<ClientJobsService>('JobsService');
  }

  async scheduleSingle(
    payload: JobScheduleSingleRequest,
    taskId: string,
  ): Promise<SingleJob> {
    const singleJob = await firstValueFrom(
      this.clientJobsService.scheduleSingle(payload),
    );

    await this.jobsRepository.save(singleJob.id, JobType.SINGLE, taskId);

    this.logger.log(
      `Sent request to schedule single job for date ${payload.executionDate} for task with id = ${taskId} to ${this.jobsClientConfig.connectionString}`,
    );

    return singleJob;
  }

  async scheduleCron(
    payload: JobScheduleCronRequest,
    taskId: string,
  ): Promise<CronJob> {
    const cronJob = await firstValueFrom(
      this.clientJobsService.scheduleCron(payload),
    );

    await this.jobsRepository.save(cronJob.id, JobType.CRON, taskId);

    this.logger.log(
      `Sent request to schedule cron job with pattern ${payload.cron} for task with id = ${taskId} to ${this.jobsClientConfig.connectionString}`,
    );

    return cronJob;
  }

  async rescheduleSingle(
    payload: JobRescheduleSingleRequest,
  ): Promise<SingleJob> {
    const singleJob = await firstValueFrom(
      this.clientJobsService.rescheduleSingle(payload),
    );

    this.logger.log(
      `Sent request to reschedule single job with id ${singleJob.id} for date ${payload.executionDate} to ${this.jobsClientConfig.connectionString}`,
    );

    return singleJob;
  }

  async rescheduleCron(payload: JobRescheduleCronRequest): Promise<CronJob> {
    const cronJob = await firstValueFrom(
      this.clientJobsService.rescheduleCron(payload),
    );

    this.logger.log(
      `Sent request to reschedule cron job with id ${cronJob.id} to pattern ${payload.cron} to ${this.jobsClientConfig.connectionString}`,
    );

    return cronJob;
  }

  async unscheduleSingle(
    payload: JobUnscheduleSingleRequest,
  ): Promise<SingleJob> {
    const singleJob = await firstValueFrom(
      this.clientJobsService.unscheduleSingle(payload),
    );

    await this.jobsRepository.remove(singleJob.id);

    this.logger.log(
      `Sent request to unschedule single job with id ${singleJob.id} to ${this.jobsClientConfig.connectionString}`,
    );

    return singleJob;
  }

  async unscheduleCron(payload: JobUnscheduleCronRequest): Promise<CronJob> {
    const cronJob = await firstValueFrom(
      this.clientJobsService.unscheduleCron(payload),
    );

    await this.jobsRepository.remove(cronJob.id);

    this.logger.log(
      `Sent request to unschedule cron job with id ${cronJob.id} to ${this.jobsClientConfig.connectionString}`,
    );

    return cronJob;
  }

  async findByTaskId(taskId: string): Promise<DbJob[]> {
    return this.jobsRepository.findByTaskId(taskId);
  }
}
