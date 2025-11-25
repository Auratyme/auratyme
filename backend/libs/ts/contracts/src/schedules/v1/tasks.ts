import { Observable } from 'rxjs';
import { SortType } from '../../common/index.js';

export type Task = {
  id: string;
  userId: string;
  scheduleId: string;
  name: string;
  description: string;
  dueTo: string;
  repeat: string;
  status: TaskStatus;
  createdAt: string;
  updatedAt: string;
  priority: number;
  fixed: boolean;
  startTime: string | null;
  endTime: string | null;
};
export type TaskEvent = {
  eventName: string;
  payload: EventPayload;
};

export enum TaskStatus {
  NOT_STARTED = 0,
  IN_PROGRESS = 1,
  DONE = 2,
  FAILED = 3,
}
export enum TasksOrderBy {
  NAME = 0,
  CREATED_AT = 1,
  UPDATED_AT = 2,
  DUE_TO = 3,
  STATUS = 4,
}

type EventFields = {
  id: string;
  userId: string;
};
type EventPayload = {
  task: EventFields;
};

type FindWhere = {
  userId?: string;
};
type FindOptions = {
  limit?: number;
  page?: number;
  orderBy?: TasksOrderBy;
  sortBy?: SortType;
};

type FindOneWhere = {
  id: string;
  userId?: string;
};

type UpdateWhere = {
  id: string;
  userId?: string;
};
type UpdateFields = {
  name?: string;
  description?: string;
  scheduleId?: string;
  dueTo?: string;
  repeat?: string;
  status?: TaskStatus;
  priority?: number;
  fixed?: boolean;
  startTime?: string | null;
  endTime?: string | null;
};

type RemoveWhere = {
  id: string;
  userId?: string;
};

export type TasksService = {
  events(payload: TaskEventsRequest): Observable<TaskEvent>;

  find(payload: TasksFindRequest): Observable<TasksFindResponse>;

  findOne(payload: TaskFindOneRequest): Observable<Task>;

  create(payload: TaskCreateRequest): Observable<Task>;

  update(payload: TaskUpdateRequest): Observable<Task>;

  remove(payload: TaskRemoveRequest): Observable<Task>;
};

export type TaskEventsRequest = {
  userId: string;
};

export type TasksFindRequest = {
  options?: FindOptions;
  where?: FindWhere;
};
export type TasksFindResponse = {
  tasks: Task[];
};

export type TaskFindOneRequest = {
  where: FindOneWhere;
};

export type TaskCreateRequest = {
  userId: string;
  scheduleId: string;
  name: string;
  description?: string | null;
  dueTo?: string | null;
  repeat?: string | null;
  status?: TaskStatus;
  priority?: number;
  fixed?: boolean;
  startTime?: string | null;
  endTime?: string | null;
};

export type TaskUpdateRequest = {
  where: UpdateWhere;
  fields?: UpdateFields;
};

export type TaskRemoveRequest = {
  where: RemoveWhere;
};

export enum TasksConfig {
  URL = 'schedules:5000',
  PACKAGE = 'task',
  PROTO_PATH = '/libs/proto/schedules/v1/tasks.proto',
  SERVICE_NAME = 'TasksService',
  EVENTS_METHOD = 'Events',
  FIND_METHOD = 'Find',
  FIND_ONE_METHOD = 'FindOne',
  CREATE_METHOD = 'Create',
  UPDATE_METHOD = 'Update',
  REMOVE_METHOD = 'Remove',
}
