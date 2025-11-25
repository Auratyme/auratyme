import { Observable } from 'rxjs';
import { SortType } from '../../common/index.js';

export type User = {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
};

export enum UsersOrderBy {
  NAME = 0,
  CREATED_AT = 1,
  UPDATED_AT = 2,
}

type FindOptions = {
  limit?: number;
  page?: number;
  orderBy?: UsersOrderBy;
  sortBy?: SortType;
};

type FindOneWhere = {
  id: string;
};

type UpdateWhere = {
  id: string;
};
type UsersUpdateFields = {
  name?: string;
};

type RemoveWhere = {
  id: string;
};

export interface UsersService {
  find(payload: UsersFindRequest): Observable<UsersFindResponse>;

  findOne(payload: UserFindOneRequest): Observable<User>;

  create(payload: UserCreateRequest): Observable<User>;

  update(payload: UserUpdateRequest): Observable<User>;

  remove(payload: UserRemoveRequest): Observable<User>;
}

export type UsersFindRequest = {
  options?: FindOptions;
};
export type UsersFindResponse = {
  users: User[];
};

export type UserFindOneRequest = {
  where: FindOneWhere;
};

export type UserCreateRequest = {
  id: string;
  name: string;
};

export type UserUpdateRequest = {
  where: UpdateWhere;
  fields?: UsersUpdateFields;
};

export type UserRemoveRequest = {
  where: RemoveWhere;
};

export enum UsersConfig {
  URL = 'users:5000',
  PROTO_PATH = '/libs/proto/users/v1/users.proto',
  PACKAGE = 'user',
  SERVICE_NAME = 'UsersService',
  FIND_METHOD = 'Find',
  FIND_ONE_METHOD = 'FindOne',
  CREATE_METHOD = 'Create',
  UPDATE_METHOD = 'Update',
  REMOVE_METHOD = 'Remove',
}
