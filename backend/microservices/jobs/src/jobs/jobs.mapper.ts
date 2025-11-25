import {
  CronJob as ClientCronJob,
  SingleJob as ClientSingleJob,
  JobType as ClientJobType,
  JobScheduleSingleRequest,
  JobScheduleCronRequest,
  JobRescheduleSingleRequest,
  JobRescheduleCronRequest,
  JobUnscheduleSingleRequest,
  JobUnscheduleCronRequest,
} from 'contracts';
import { SingleJob, CronJob } from './entities';
import { JobType } from './enums';
import {
  JobRescheduleCronDto,
  JobRescheduleSingleDto,
  JobScheduleCronDto,
  JobScheduleSingleDto,
  JobUnscheduleCronDto,
  JobUnscheduleSingleDto,
} from './dtos';

export class JobsMapper {
  static clientCronJobToDomain(clientCronJob: ClientCronJob): CronJob {
    return {
      ...clientCronJob,
      type:
        clientCronJob.type === ClientJobType.CRON
          ? JobType.CRON
          : JobType.SINGLE,
    };
  }
  static domainCronJobToClient(cronJob: CronJob): ClientCronJob {
    return {
      ...cronJob,
      type:
        cronJob.type === JobType.CRON
          ? ClientJobType.CRON
          : ClientJobType.SINGLE,
    };
  }

  static clientSingleJobToDomain(clientSingleJob: ClientSingleJob): SingleJob {
    return {
      ...clientSingleJob,
      type:
        clientSingleJob.type === ClientJobType.CRON
          ? JobType.CRON
          : JobType.SINGLE,
    };
  }
  static domainSingleJobToClient(singleJob: SingleJob): ClientSingleJob {
    return {
      ...singleJob,
      type:
        singleJob.type === JobType.CRON
          ? ClientJobType.CRON
          : ClientJobType.SINGLE,
    };
  }

  static scheduleSingleRequestToDto(
    request: JobScheduleSingleRequest,
  ): JobScheduleSingleDto {
    return request;
  }
  static scheduleSingleDtoToRequest(
    dto: JobScheduleSingleDto,
  ): JobScheduleSingleRequest {
    return dto;
  }

  static scheduleCronRequestToDto(
    request: JobScheduleCronRequest,
  ): JobScheduleCronDto {
    return request;
  }
  static scheduleCronDtoToRequest(
    dto: JobScheduleCronDto,
  ): JobScheduleCronRequest {
    return dto;
  }

  static rescheduleSingleRequestToDto(
    request: JobRescheduleSingleRequest,
  ): JobRescheduleSingleDto {
    return request;
  }
  static rescheduleSingleDtoToRequest(
    dto: JobRescheduleSingleDto,
  ): JobRescheduleSingleRequest {
    return dto;
  }

  static rescheduleCronRequestToDto(
    request: JobRescheduleCronRequest,
  ): JobRescheduleCronDto {
    return request;
  }
  static rescheduleCronDtoToRequest(
    dto: JobRescheduleCronDto,
  ): JobRescheduleCronRequest {
    return dto;
  }

  static unscheduleSingleRequestToDto(
    request: JobUnscheduleSingleRequest,
  ): JobUnscheduleSingleDto {
    return request;
  }
  static unscheduleSingleDtoToRequest(
    dto: JobUnscheduleSingleDto,
  ): JobUnscheduleSingleRequest {
    return dto;
  }

  static unscheduleCronRequestToDto(
    request: JobUnscheduleCronRequest,
  ): JobUnscheduleCronDto {
    return request;
  }
  static unscheduleCronDtoToRequest(
    dto: JobUnscheduleCronDto,
  ): JobUnscheduleCronRequest {
    return dto;
  }
}
