import { Observable } from 'rxjs';
import { SortType } from '../../common/index.js';

export type Schedule = {
  id: string;
  userId: string;
  name: string;
  description: string | null;
  createdAt: string;
  updatedAt: string;
};

export enum SchedulesOrderBy {
  NAME = 0,
  CREATED_AT = 1,
  UPDATED_AT = 2,
}

type FindWhere = {
  userId?: string;
};
type FindOptions = {
  orderBy?: SchedulesOrderBy;
  sortBy?: SortType;
  limit?: number;
  page?: number;
};

type FindOneWhere = { id: string; userId?: string };

type UpdateWhere = {
  id: string;
  userId?: string;
};
type UpdateFields = {
  name?: string;
  description?: string | null;
};

type RemoveWhere = {
  id: string;
  userId?: string;
};
type RemoveOptions = {
  force?: boolean;
};

export type SchedulesService = {
  find(payload: SchedulesFindRequest): Observable<SchedulesFindResponse>;

  findOne(payload: ScheduleFindOneRequest): Observable<Schedule>;

  create(payload: ScheduleCreateRequest): Observable<Schedule>;

  update(payload: ScheduleUpdateRequest): Observable<Schedule>;

  remove(payload: ScheduleRemoveRequest): Observable<Schedule>;
};

export type SchedulesFindRequest = {
  options?: FindOptions;
  where?: FindWhere;
};
export type SchedulesFindResponse = {
  schedules: Schedule[];
};

export type ScheduleFindOneRequest = {
  where: FindOneWhere;
};

export type ScheduleCreateRequest = {
  name: string;
  description?: string | null;
  userId: string;
};

export type ScheduleUpdateRequest = {
  where: UpdateWhere;
  fields?: UpdateFields;
};

export type ScheduleRemoveRequest = {
  where: RemoveWhere;
  options?: RemoveOptions;
};

export enum SchedulesConfig {
  URL = 'schedules:5000',
  PACKAGE = 'schedule',
  PROTO_PATH = '/libs/proto/schedules/v1/schedules.proto',
  SERVICE_NAME = 'SchedulesService',
  FIND_METHOD = 'Find',
  FIND_ONE_METHOD = 'FindOne',
  CREATE_METHOD = 'Create',
  UPDATE_METHOD = 'Update',
  REMOVE_METHOD = 'Remove',
}
