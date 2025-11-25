import {
  Controller,
  Logger,
  UseFilters,
  UseInterceptors,
} from '@nestjs/common';
import { GrpcMethod, Payload, RpcException } from '@nestjs/microservices';

import { JobsService } from './jobs.service';
import {
  JobRescheduleSingleRequest,
  JobRescheduleCronRequest,
  JobScheduleCronRequest,
  JobScheduleSingleRequest,
  JobUnscheduleCronRequest,
  JobUnscheduleSingleRequest,
  CronJob,
  SingleJob,
  JobsConfig,
} from 'contracts';
import { JobsMapper } from './jobs.mapper';
import { RpcExceptionFilter, RpcRequestInterceptor } from 'common';
import { JobException } from './exceptions';
import { status as GrpcStatus } from '@grpc/grpc-js';

@UseFilters(RpcExceptionFilter)
@UseInterceptors(RpcRequestInterceptor)
@Controller()
export class JobsController {
  private readonly logger = new Logger(JobsController.name);

  constructor(private readonly jobsService: JobsService) {}

  @GrpcMethod(JobsConfig.SERVICE_NAME, JobsConfig.SCHEDULE_SINGLE_METHOD)
  async scheduleSingle(
    @Payload() payload: JobScheduleSingleRequest,
  ): Promise<SingleJob> {
    try {
      const singleJob = await this.jobsService.scheduleSingle(
        JobsMapper.scheduleSingleRequestToDto(payload),
      );

      return JobsMapper.domainSingleJobToClient(singleJob);
    } catch (err) {
      const error = err as JobException;

      throw new RpcException({
        message: error.message,
        code: GrpcStatus.INTERNAL,
        cause: error,
      });
    }
  }

  @GrpcMethod(JobsConfig.SERVICE_NAME, JobsConfig.SCHEDULE_CRON_METHOD)
  async scheduleCron(
    @Payload() payload: JobScheduleCronRequest,
  ): Promise<CronJob> {
    try {
      const cronJob = await this.jobsService.scheduleCron(
        JobsMapper.scheduleCronRequestToDto(payload),
      );

      return JobsMapper.domainCronJobToClient(cronJob);
    } catch (err) {
      const error = err as JobException;

      throw new RpcException({
        message: error.message,
        code: GrpcStatus.INTERNAL,
        cause: error,
      });
    }
  }

  @GrpcMethod(JobsConfig.SERVICE_NAME, JobsConfig.RESCHEDULE_SINGLE_METHOD)
  async rescheduleSingle(
    @Payload() payload: JobRescheduleSingleRequest,
  ): Promise<SingleJob> {
    try {
      const singleJob = await this.jobsService.rescheduleSingle(
        JobsMapper.rescheduleSingleRequestToDto(payload),
      );

      return JobsMapper.domainSingleJobToClient(singleJob);
    } catch (err) {
      const error = err as JobException;

      throw new RpcException({
        message: error.message,
        code: GrpcStatus.INTERNAL,
        cause: error,
      });
    }
  }

  @GrpcMethod(JobsConfig.SERVICE_NAME, JobsConfig.RESCHEDULE_CRON_METHOD)
  async rescheduleCron(
    @Payload() payload: JobRescheduleCronRequest,
  ): Promise<CronJob> {
    try {
      const cronJob = await this.jobsService.rescheduleCron(
        JobsMapper.rescheduleCronRequestToDto(payload),
      );

      return JobsMapper.domainCronJobToClient(cronJob);
    } catch (err) {
      const error = err as JobException;

      throw new RpcException({
        message: error.message,
        code: GrpcStatus.INTERNAL,
        cause: error,
      });
    }
  }

  @GrpcMethod(JobsConfig.SERVICE_NAME, JobsConfig.UNSCHEDULE_SINGLE_METHOD)
  async unscheduleSingle(
    @Payload() payload: JobUnscheduleSingleRequest,
  ): Promise<SingleJob> {
    try {
      const singleJob = await this.jobsService.unscheduleSingle(
        JobsMapper.unscheduleSingleRequestToDto(payload),
      );

      return JobsMapper.domainSingleJobToClient(singleJob);
    } catch (err) {
      const error = err as JobException;

      throw new RpcException({
        message: error.message,
        code: GrpcStatus.INTERNAL,
        cause: error,
      });
    }
  }

  @GrpcMethod(JobsConfig.SERVICE_NAME, JobsConfig.UNSCHEDULE_CRON_METHOD)
  async unscheduleCron(
    @Payload() payload: JobUnscheduleCronRequest,
  ): Promise<CronJob> {
    try {
      const cronJob = await this.jobsService.unscheduleCron(
        JobsMapper.unscheduleCronRequestToDto(payload),
      );

      return JobsMapper.domainCronJobToClient(cronJob);
    } catch (err) {
      const error = err as JobException;

      throw new RpcException({
        message: error.message,
        code: GrpcStatus.INTERNAL,
        cause: error,
      });
    }
  }
}
