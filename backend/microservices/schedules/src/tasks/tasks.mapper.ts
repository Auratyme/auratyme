import {
  TasksFindDto,
  TaskUpdateDto,
  TaskCreateDto,
  TaskFindOneDto,
  TaskRemoveDto,
} from './dtos';
import { Task } from './entities';
import { DbTask } from './types';
import { TaskStatus } from './enums';
import {
  TaskStatus as ClientTaskStatus,
  Task as ClientTask,
  TasksFindRequest,
  SortType,
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskFindOneRequest,
  TaskRemoveRequest,
  TasksOrderBy,
} from 'contracts';
import { TasksOrderByFields } from './types/helpers';
import { doesNotReject } from 'assert';

export class TasksMapper {
  static clientOrderByToDomain(
    clientOrderBy: TasksOrderBy,
  ): TasksOrderByFields {
    switch (clientOrderBy) {
      case TasksOrderBy.NAME:
        return 'name';
      case TasksOrderBy.CREATED_AT:
        return 'createdAt';
      case TasksOrderBy.UPDATED_AT:
        return 'updatedAt';
      case TasksOrderBy.DUE_TO:
        return 'dueTo';
      case TasksOrderBy.STATUS:
        return 'status';
    }
  }
  static domainOrderByToClient(orderBy: TasksOrderByFields): TasksOrderBy {
    switch (orderBy) {
      case 'name':
        return TasksOrderBy.NAME;
      case 'createdAt':
        return TasksOrderBy.CREATED_AT;
      case 'status':
        return TasksOrderBy.STATUS;
      case 'dueTo':
        return TasksOrderBy.DUE_TO;
      case 'updatedAt':
        return TasksOrderBy.UPDATED_AT;
    }
  }

  static dbToDomain(dbTask: DbTask): Task {
    return {
      ...dbTask,
      createdAt: dbTask.createdAt.toISOString(),
      updatedAt: dbTask.updatedAt.toISOString(),
      dueTo: dbTask.dueTo ? dbTask.dueTo.toISOString() : null,
    };
  }

  static clientToDomain(clientTask: ClientTask): Task {
    return {
      ...clientTask,
      description:
        clientTask.description?.length === 0 ? null : clientTask.description,
      dueTo: clientTask.dueTo?.length === 0 ? null : clientTask.dueTo,
      repeat: clientTask.repeat?.length === 0 ? null : clientTask.repeat,
      status: this.clientToDomainStatus(clientTask.status),
    };
  }
  static domainToClient(task: Task): ClientTask {
    return {
      ...task,
      startTime: task.startTime === null ? '' : task.startTime,
      endTime: task.endTime === null ? '' : task.endTime,
      description: task.description === null ? '' : task.description,
      dueTo: task.dueTo === null ? '' : task.dueTo,
      repeat: task.repeat === null ? '' : task.repeat,
      status: this.domainToClientStatus(task.status),
    };
  }

  static findRequestToFindDto(request?: TasksFindRequest): TasksFindDto {
    return {
      options: {
        limit: request?.options?.limit,
        orderBy: request?.options?.orderBy
          ? this.clientOrderByToDomain(request?.options?.orderBy)
          : undefined,
        page: request?.options?.page,
        sortBy: request?.options?.sortBy === SortType.ASC ? 'asc' : 'desc',
      },
      where: {
        userId: request?.where?.userId,
      },
    };
  }

  static findDtoToFindRequest(dto?: TasksFindDto): TasksFindRequest {
    return {
      options: {
        limit: dto?.options?.limit,
        orderBy: dto?.options?.orderBy
          ? this.domainOrderByToClient(dto?.options?.orderBy)
          : undefined,
        sortBy: dto?.options?.sortBy === 'asc' ? SortType.ASC : SortType.DESC,
        page: dto?.options?.page,
      },
      where: {
        userId: dto?.where?.userId,
      },
    };
  }

  static findOneRequestToFindOneDto(
    request: TaskFindOneRequest,
  ): TaskFindOneDto {
    return request;
  }
  static findOneDtoToFindOneRequest(dto: TaskFindOneDto): TaskFindOneRequest {
    return dto;
  }

  static createRequestToCreateDto(request: TaskCreateRequest): TaskCreateDto {
    return {
      ...request,
      status: this.clientToDomainStatus(
        request.status || ClientTaskStatus.NOT_STARTED,
      ),
      description: request.description,
      dueTo: request.dueTo,
      repeat: request.repeat,
    };
  }
  static createDtoToCreateRequest(dto: TaskCreateDto): TaskCreateRequest {
    return {
      ...dto,
      status: dto.status ? this.domainToClientStatus(dto.status) : undefined,
      description: dto.description,
      dueTo: dto.dueTo,
      repeat: dto.repeat,
      startTime: dto.startTime,
      endTime: dto.endTime,
    };
  }

  static updateRequestToUpdateDto(request: TaskUpdateRequest): TaskUpdateDto {
    return {
      ...request,
      fields: {
        ...request.fields,
        status: this.clientToDomainStatus(
          request.fields?.status || ClientTaskStatus.NOT_STARTED,
        ),
        description: request.fields?.description,
        dueTo: request.fields?.dueTo,
        repeat: request.fields?.repeat,
      },
    };
  }
  static updateDtoToUpdateRequest(dto: TaskUpdateDto): TaskUpdateRequest {
    return {
      ...dto,
      fields: {
        ...dto.fields,
        status: this.domainToClientStatus(
          dto.fields?.status || TaskStatus.NOT_STARTED,
        ),
        description:
          dto.fields?.description === null ? '' : dto.fields?.description,
        dueTo: dto.fields?.dueTo === null ? '' : dto.fields?.dueTo,
        repeat: dto.fields?.repeat === null ? '' : dto.fields?.repeat,
      },
    };
  }

  static removeRequestToRemoveDto(request: TaskRemoveRequest): TaskRemoveDto {
    return request;
  }
  static removeDtoToRemoveRequest(dto: TaskRemoveDto): TaskRemoveRequest {
    return dto;
  }

  private static domainToClientStatus(
    status: (typeof TaskStatus)[keyof typeof TaskStatus],
  ): ClientTaskStatus {
    switch (status) {
      case 'not-started':
        return ClientTaskStatus.NOT_STARTED;
      case 'in-progress':
        return ClientTaskStatus.IN_PROGRESS;
      case 'done':
        return ClientTaskStatus.DONE;
      case 'failed':
        return ClientTaskStatus.FAILED;
    }
  }

  private static clientToDomainStatus(
    clientStatus: ClientTaskStatus,
  ): (typeof TaskStatus)[keyof typeof TaskStatus] {
    switch (clientStatus) {
      case ClientTaskStatus.NOT_STARTED:
        return 'not-started';
      case ClientTaskStatus.IN_PROGRESS:
        return 'in-progress';
      case ClientTaskStatus.DONE:
        return 'done';
      case ClientTaskStatus.FAILED:
        return 'failed';
    }
  }
}
