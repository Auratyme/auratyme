import {
  ScheduleResponseDto,
  ScheduleCreateDto,
  ScheduleFindOneDto,
  ScheduleRemoveDto,
  ScheduleUpdateDto,
  SchedulesFindDto,
} from './dtos';
import { Schedule } from './entities';
import { DbSchedule } from './types';
import {
  Schedule as ClientSchedule,
  SchedulesFindResponse,
  ScheduleFindOneRequest,
  ScheduleCreateRequest,
  ScheduleUpdateRequest,
  ScheduleRemoveRequest,
  SchedulesFindRequest,
  SortType,
  SchedulesOrderBy,
} from 'contracts';
import { SchedulesOrderByFields } from './types/helpers';

export class SchedulesMapper {
  static clientOrderByToDomain(
    clientOrderBy: SchedulesOrderBy,
  ): SchedulesOrderByFields {
    switch (clientOrderBy) {
      case SchedulesOrderBy.NAME:
        return 'name';
      case SchedulesOrderBy.CREATED_AT:
        return 'createdAt';
      case SchedulesOrderBy.UPDATED_AT:
        return 'updatedAt';
    }
  }
  static domainOrderByToClient(
    orderBy: SchedulesOrderByFields,
  ): SchedulesOrderBy {
    switch (orderBy) {
      case 'name':
        return SchedulesOrderBy.NAME;
      case 'createdAt':
        return SchedulesOrderBy.CREATED_AT;
      case 'updatedAt':
        return SchedulesOrderBy.UPDATED_AT;
    }
  }

  static dbToDomain(dbSchedule: DbSchedule): Schedule {
    return {
      createdAt: dbSchedule.createdAt.toISOString(),
      updatedAt: dbSchedule.updatedAt.toISOString(),
      description: dbSchedule.description,
      id: dbSchedule.id,
      name: dbSchedule.name,
      userId: dbSchedule.userId,
    };
  }

  static domainToResponseDto(schedule: Schedule): ScheduleResponseDto {
    return {
      createdAt: schedule.createdAt,
      description: schedule.description,
      id: schedule.id,
      name: schedule.name,
      updatedAt: schedule.updatedAt,
      userId: schedule.userId,
    };
  }

  static clientToDomain(clientSchedule: ClientSchedule): Schedule {
    return {
      ...clientSchedule,
      description: clientSchedule.description,
    };
  }
  static domainToClient(schedule: Schedule): ClientSchedule {
    return {
      ...schedule,
      description: schedule.description === null ? '' : schedule.description,
    };
  }

  static findDtoToFindRequest(dto: SchedulesFindDto): SchedulesFindRequest {
    return {
      ...dto,
      options: {
        ...dto.options,
        sortBy: dto.options?.sortBy === 'asc' ? SortType.ASC : SortType.DESC,
        orderBy: dto.options?.orderBy
          ? this.domainOrderByToClient(dto.options?.orderBy)
          : undefined,
      },
    };
  }
  static findRequestToFindDto(request: SchedulesFindRequest): SchedulesFindDto {
    return {
      ...request,
      options: {
        ...request.options,
        sortBy: request.options?.sortBy === SortType.ASC ? 'asc' : 'desc',
        orderBy: request.options?.orderBy
          ? this.clientOrderByToDomain(request.options.orderBy)
          : undefined,
      },
    };
  }

  static findOneDtoToFindOneRequest(
    dto: ScheduleFindOneDto,
  ): ScheduleFindOneRequest {
    return dto;
  }
  static findOneRequestToFindOneDto(
    request: ScheduleFindOneRequest,
  ): ScheduleFindOneDto {
    return request;
  }

  static createDtoToCreateRequest(
    dto: ScheduleCreateDto,
  ): ScheduleCreateRequest {
    return {
      ...dto,
      description: dto.description === null ? '' : dto.description,
    };
  }
  static createRequestToCreateDto(
    request: ScheduleCreateRequest,
  ): ScheduleCreateDto {
    return {
      ...request,
      description: request.description,
    };
  }

  static updateDtoToUpdateRequest(
    dto: ScheduleUpdateDto,
  ): ScheduleUpdateRequest {
    return {
      ...dto,
      fields: {
        ...dto.fields,
        description:
          dto.fields?.description === null ? '' : dto.fields?.description,
      },
    };
  }
  static updateRequestToUpdateDto(
    request: ScheduleUpdateRequest,
  ): ScheduleUpdateDto {
    return {
      ...request,
      fields: {
        ...request.fields,
        description:
          request.fields?.description?.length === 0
            ? null
            : request.fields?.description,
      },
    };
  }

  static removeDtoToRemoveRequest(
    dto: ScheduleRemoveDto,
  ): ScheduleRemoveRequest {
    return dto;
  }
  static removeRequestToRemoveDto(
    request: ScheduleRemoveRequest,
  ): ScheduleRemoveDto {
    return request;
  }
}
