import { Inject, Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { type ClientGrpc } from '@nestjs/microservices';
import {
  TasksService as ClientTasksService,
  TaskCreateRequest,
  TaskFindOneRequest,
  TaskRemoveRequest,
  TasksFindRequest,
  TaskUpdateRequest,
  Task,
  TasksFindResponse,
  TaskEventsRequest,
  TaskEvent,
  TasksConfig,
} from 'contracts';
import { catchError, firstValueFrom, Observable } from 'rxjs';
import { DiToken } from '../common/enums';
import { TaskException, TaskNotFoundException } from './exceptions';
import { GrpcNotFoundException, throwGrpcException } from 'common';
import { ScheduleNotFoundException } from '../schedules/exceptions';

@Injectable()
export class TasksService implements OnModuleInit {
  private tasksService: ClientTasksService;
  private logger = new Logger(TasksService.name);

  constructor(@Inject(DiToken.TASK_PACKAGE) private client: ClientGrpc) {}

  onModuleInit() {
    this.tasksService = this.client.getService<ClientTasksService>(
      TasksConfig.SERVICE_NAME,
    );
  }

  events(payload: TaskEventsRequest): Observable<TaskEvent> {
    return this.tasksService.events(payload);
  }

  async find(payload: TasksFindRequest): Promise<TasksFindResponse> {
    try {
      const result = await firstValueFrom(
        this.tasksService.find(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      throw new TaskException('error while finding tasks', err, '');
    }
  }

  async findOne(payload: TaskFindOneRequest): Promise<Task> {
    try {
      const result = await firstValueFrom(
        this.tasksService.findOne(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      if (err instanceof GrpcNotFoundException) {
        throw new TaskNotFoundException(payload.where.id);
      }

      throw new TaskException('error while finding one task', err, '');
    }
  }

  async create(payload: TaskCreateRequest): Promise<Task> {
    try {
      const result = await firstValueFrom(
        this.tasksService.create(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      if (err instanceof GrpcNotFoundException) {
        throw new ScheduleNotFoundException(payload.scheduleId);
      }

      throw new TaskException('error while creating task', err, '');
    }
  }

  async update(payload: TaskUpdateRequest): Promise<Task> {
    try {
      const result = await firstValueFrom(
        this.tasksService.update(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      if (err instanceof GrpcNotFoundException) {
        throw new TaskNotFoundException(payload.where.id);
      }

      throw new TaskException('error while updating task', err, '');
    }
  }

  async remove(payload: TaskRemoveRequest): Promise<Task> {
    try {
      const result = await firstValueFrom(
        this.tasksService.remove(payload).pipe(
          catchError((err) => {
            return throwGrpcException(err.code, err);
          }),
        ),
      );

      return result;
    } catch (err) {
      if (err instanceof GrpcNotFoundException) {
        throw new TaskNotFoundException(payload.where.id);
      }

      throw new TaskException('error while removing task', err, '');
    }
  }
}
