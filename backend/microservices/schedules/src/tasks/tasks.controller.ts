import {
  Controller,
  Logger,
  UseFilters,
  UseInterceptors,
} from '@nestjs/common';
import { GrpcMethod, Payload } from '@nestjs/microservices';
import { TasksService } from './tasks.service';
import { RpcExceptionFilter, RpcRequestInterceptor } from 'common';
import {
  taskCreateSchema,
  taskEventsSchema,
  taskFindOneSchema,
  taskRemoveSchema,
  taskUpdateSchema,
  tasksFindSchema,
} from './schemas';
import { RpcValidationPipe } from 'common';
import { z } from 'zod';
import {
  TasksFindResponse,
  Task,
  TaskEvent as ClientTaskEvent,
  TasksConfig,
} from 'contracts';
import { TasksMapper } from './tasks.mapper';
import { TaskNotFoundException } from './exceptions';
import { ScheduleNotFoundException } from '../schedules/exceptions';
import { Observable, filter } from 'rxjs';
import { EventsService } from '../events/events.service';
import { TaskEventPayload } from './types';
import { TaskEvent } from './enums';
import { GrpcInternalException, GrpcNotFoundException } from 'common';

@UseFilters(RpcExceptionFilter)
@UseInterceptors(RpcRequestInterceptor)
@Controller()
export class TasksController {
  private readonly logger = new Logger(TasksController.name);

  constructor(
    private readonly tasksService: TasksService,
    private readonly eventsService: EventsService<TaskEventPayload>,
  ) {}

  @GrpcMethod(TasksConfig.SERVICE_NAME, TasksConfig.EVENTS_METHOD)
  events(
    @Payload(new RpcValidationPipe(taskEventsSchema))
    payload: z.infer<typeof taskEventsSchema>,
  ): Observable<ClientTaskEvent> {
    const userId = payload?.userId;

    return this.eventsService.consume(TaskEvent.ALL).pipe(
      filter((payload) => {
        if (userId) {
          return payload.payload.task.userId === userId;
        }

        return true;
      }),
    );
  }

  @GrpcMethod(TasksConfig.SERVICE_NAME, TasksConfig.FIND_METHOD)
  async find(
    @Payload(new RpcValidationPipe(tasksFindSchema))
    payload: z.infer<typeof tasksFindSchema>,
  ): Promise<TasksFindResponse> {
    try {
      const tasks = await this.tasksService.find(
        TasksMapper.findRequestToFindDto(payload),
      );

      return {
        tasks: tasks.map((task) => TasksMapper.domainToClient(task)),
      };
    } catch (err) {
      throw new GrpcInternalException(
        'unknown error occured while finding tasks',
        null,
        err,
      );
    }
  }

  @GrpcMethod(TasksConfig.SERVICE_NAME, TasksConfig.FIND_ONE_METHOD)
  async findOne(
    @Payload(new RpcValidationPipe(taskFindOneSchema))
    payload: z.infer<typeof taskFindOneSchema>,
  ): Promise<Task> {
    try {
      const task = await this.tasksService.findOne(
        TasksMapper.findOneRequestToFindOneDto(payload),
      );

      return TasksMapper.domainToClient(task);
    } catch (err) {
      if (err instanceof TaskNotFoundException) {
        throw new GrpcNotFoundException('task not found', null);
      }

      throw new GrpcInternalException(
        'unknown error occured while finding one task',
        null,
        err,
      );
    }
  }

  @GrpcMethod(TasksConfig.SERVICE_NAME, TasksConfig.CREATE_METHOD)
  async create(
    @Payload(new RpcValidationPipe(taskCreateSchema))
    payload: z.infer<typeof taskCreateSchema>,
  ): Promise<Task> {
    try {
      const createdTask = await this.tasksService.create(
        TasksMapper.createRequestToCreateDto(payload),
      );

      return TasksMapper.domainToClient(createdTask);
    } catch (err) {
      if (err instanceof ScheduleNotFoundException) {
        throw new GrpcNotFoundException('schedule not found', null);
      }

      throw new GrpcInternalException(
        'unknown error occured while creating task',
        null,
        err,
      );
    }
  }

  @GrpcMethod(TasksConfig.SERVICE_NAME, TasksConfig.UPDATE_METHOD)
  async update(
    @Payload(new RpcValidationPipe(taskUpdateSchema))
    payload: z.infer<typeof taskUpdateSchema>,
  ): Promise<Task> {
    try {
      const updatedTask = await this.tasksService.update(
        TasksMapper.updateRequestToUpdateDto(payload),
      );

      return TasksMapper.domainToClient(updatedTask);
    } catch (err) {
      if (err instanceof TaskNotFoundException) {
        throw new GrpcNotFoundException('task not found', null);
      }

      if (err instanceof ScheduleNotFoundException) {
        throw new GrpcNotFoundException('schedule not found', null);
      }

      throw new GrpcInternalException(
        'unknown error occured while updating task',
        null,
        err,
      );
    }
  }

  @GrpcMethod(TasksConfig.SERVICE_NAME, TasksConfig.REMOVE_METHOD)
  async remove(
    @Payload(new RpcValidationPipe(taskRemoveSchema))
    payload: z.infer<typeof taskRemoveSchema>,
  ): Promise<Task> {
    try {
      const removedTask = await this.tasksService.remove(
        TasksMapper.removeRequestToRemoveDto(payload),
      );

      return TasksMapper.domainToClient(removedTask);
    } catch (err) {
      if (err instanceof TaskNotFoundException) {
        throw new GrpcNotFoundException('task not found', null);
      }

      throw new GrpcInternalException(
        'unknown error occured while updating schedule',
        null,
        err,
      );
    }
  }
}
