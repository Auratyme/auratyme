import {
  Controller,
  Logger,
  UseFilters,
  UseInterceptors,
} from '@nestjs/common';
import { SchedulesService } from './schedules.service';
import { GrpcMethod, Payload } from '@nestjs/microservices';
import { Schedule, SchedulesConfig, SchedulesFindResponse } from 'contracts';
import { SchedulesMapper } from './schedules.mapper';
import {
  ScheduleCannotBeDeletedException,
  ScheduleNotFoundException,
} from './exceptions';
import {
  GrpcFailedPreconditionException,
  GrpcInternalException,
  GrpcNotFoundException,
  RpcExceptionFilter,
  RpcRequestInterceptor,
  RpcValidationPipe,
} from 'common';
import {
  scheduleCreateSchema,
  scheduleFindOneSchema,
  scheduleRemoveSchema,
  schedulesFindSchema,
  scheduleUpdateSchema,
} from './schemas';
import { z } from 'zod';

@UseFilters(RpcExceptionFilter)
@UseInterceptors(RpcRequestInterceptor)
@Controller()
export class SchedulesController {
  private readonly logger = new Logger(SchedulesController.name);

  constructor(private readonly schedulesService: SchedulesService) {}

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.FIND_METHOD)
  async find(
    @Payload(new RpcValidationPipe(schedulesFindSchema))
    payload: z.infer<typeof schedulesFindSchema>,
  ): Promise<SchedulesFindResponse> {
    try {
      const schedules = await this.schedulesService.find(
        SchedulesMapper.findRequestToFindDto(payload),
      );

      return {
        schedules: schedules.map(SchedulesMapper.domainToClient),
      };
    } catch (err) {
      throw new GrpcInternalException(
        'unknown error occured while finding schedules',
        null,
        err,
      );
    }
  }

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.FIND_ONE_METHOD)
  async findOne(
    @Payload(new RpcValidationPipe(scheduleFindOneSchema))
    payload: z.infer<typeof scheduleFindOneSchema>,
  ): Promise<Schedule> {
    try {
      const schedule = await this.schedulesService.findOne(
        SchedulesMapper.findOneRequestToFindOneDto(payload),
      );

      return SchedulesMapper.domainToClient(schedule);
    } catch (err) {
      if (err instanceof ScheduleNotFoundException) {
        throw new GrpcNotFoundException('schedule not found', null);
      }

      throw new GrpcInternalException(
        'unknown error occured while finding one schedule',
        null,
        err,
      );
    }
  }

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.CREATE_METHOD)
  async create(
    @Payload(new RpcValidationPipe(scheduleCreateSchema))
    payload: z.infer<typeof scheduleCreateSchema>,
  ): Promise<Schedule> {
    try {
      const createdSchedule = await this.schedulesService.create(
        SchedulesMapper.createRequestToCreateDto(payload),
      );

      return SchedulesMapper.domainToClient(createdSchedule);
    } catch (err) {
      throw new GrpcInternalException(
        'unknown error occured while creating schedule',
        null,
        err,
      );
    }
  }

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.UPDATE_METHOD)
  async update(
    @Payload(new RpcValidationPipe(scheduleUpdateSchema))
    payload: z.infer<typeof scheduleUpdateSchema>,
  ): Promise<Schedule> {
    try {
      const updatedSchedule = await this.schedulesService.update(
        SchedulesMapper.updateRequestToUpdateDto(payload),
      );

      return SchedulesMapper.domainToClient(updatedSchedule);
    } catch (err) {
      if (err instanceof ScheduleNotFoundException) {
        if (err instanceof ScheduleNotFoundException) {
          throw new GrpcNotFoundException('schedule not found', null);
        }
      }

      throw new GrpcInternalException(
        'unknown error occured while updating schedule',
        null,
        err,
      );
    }
  }

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.REMOVE_METHOD)
  async remove(
    @Payload(new RpcValidationPipe(scheduleRemoveSchema))
    payload: z.infer<typeof scheduleRemoveSchema>,
  ): Promise<Schedule> {
    try {
      const removedSchedule = await this.schedulesService.remove(
        SchedulesMapper.removeRequestToRemoveDto(payload),
      );

      return SchedulesMapper.domainToClient(removedSchedule);
    } catch (err) {
      if (err instanceof ScheduleNotFoundException) {
        throw new GrpcNotFoundException('schedule not found', null);
      }

      if (err instanceof ScheduleCannotBeDeletedException) {
        throw new GrpcFailedPreconditionException(
          'schedule cannot be deleted because it has tasks',
          null,
          err,
        );
      }

      throw new GrpcInternalException(
        'unknown error occured while removing schedule',
        null,
        err,
      );
    }
  }
}
