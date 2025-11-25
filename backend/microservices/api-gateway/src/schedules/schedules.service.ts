import { Inject, Injectable, OnModuleInit } from '@nestjs/common';
import { type ClientGrpc } from '@nestjs/microservices';
import {
  SchedulesService as ISchedulesService,
  Schedule,
  ScheduleCreateRequest,
  ScheduleFindOneRequest,
  ScheduleRemoveRequest,
  SchedulesConfig,
  SchedulesFindRequest,
  SchedulesFindResponse,
  ScheduleUpdateRequest,
} from 'contracts';
import { firstValueFrom, catchError } from 'rxjs';
import { DiToken } from '../common/enums';
import {
  ScheduleCannotBeDeletedException,
  ScheduleException,
  ScheduleNotFoundException,
} from './exceptions';
import { GrpcFailedPreconditionException, GrpcNotFoundException } from 'common';
import { throwGrpcException } from 'common';

@Injectable()
export class SchedulesService implements OnModuleInit {
  private schedulesService: ISchedulesService;

  constructor(@Inject(DiToken.SCHEDULE_PACKAGE) private client: ClientGrpc) {}

  onModuleInit() {
    this.schedulesService = this.client.getService<ISchedulesService>(
      SchedulesConfig.SERVICE_NAME,
    );
  }

  async find(payload: SchedulesFindRequest): Promise<SchedulesFindResponse> {
    try {
      const result = await firstValueFrom(
        this.schedulesService.find(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      throw new ScheduleException('error while finding schedules', err, '');
    }
  }

  async findOne(payload: ScheduleFindOneRequest): Promise<Schedule> {
    try {
      const result = await firstValueFrom(
        this.schedulesService.findOne(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      if (err instanceof GrpcNotFoundException) {
        throw new ScheduleNotFoundException(payload.where.id);
      }

      throw new ScheduleException(
        'error while finding one schedule',
        err,
        payload.where.id,
      );
    }
  }

  async create(payload: ScheduleCreateRequest): Promise<Schedule> {
    try {
      const result = await firstValueFrom(
        this.schedulesService.create(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      throw new ScheduleException('error while creating schedule', err, '');
    }
  }

  async update(payload: ScheduleUpdateRequest): Promise<Schedule> {
    try {
      const result = await firstValueFrom(
        this.schedulesService.update(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      if (err instanceof GrpcNotFoundException) {
        throw new ScheduleNotFoundException(payload.where.id);
      }

      throw new ScheduleException(
        'error while updating schedule',
        err,
        payload.where.id,
      );
    }
  }

  async remove(payload: ScheduleRemoveRequest): Promise<Schedule> {
    try {
      const result = await firstValueFrom(
        this.schedulesService.remove(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      if (err instanceof GrpcNotFoundException) {
        throw new ScheduleNotFoundException(payload.where.id);
      }

      if (err instanceof GrpcFailedPreconditionException) {
        throw new ScheduleCannotBeDeletedException(payload.where.id);
      }

      throw new ScheduleException(
        'error while removing schedule',
        err,
        payload.where.id,
      );
    }
  }
}
