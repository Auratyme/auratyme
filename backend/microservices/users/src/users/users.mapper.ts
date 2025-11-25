import { UsersFindDto } from './dtos';
import { User } from './entities';
import { DbUser } from './types/db.type';
import {
  User as ClientUser,
  SortType,
  UsersFindRequest,
  UsersOrderBy,
} from 'contracts';
import { UsersOrderByFields } from './types/helpers';

export class UsersMapper {
  static dbToDomain(dbUser: DbUser): User {
    return {
      ...dbUser,
      createdAt: dbUser.createdAt.toISOString(),
      updatedAt: dbUser.updatedAt.toISOString(),
    };
  }

  static clientToDomain(clientUser: ClientUser): User {
    return clientUser;
  }
  static domainToClient(user: User): ClientUser {
    return user;
  }

  static findRequestToDto(request: UsersFindRequest): UsersFindDto {
    return {
      ...request,
      options: {
        ...request.options,
        orderBy: request.options?.orderBy
          ? this.clientOrderByToDomain(request.options?.orderBy)
          : undefined,
        sortBy: request.options?.sortBy === SortType.ASC ? 'asc' : 'desc',
      },
    };
  }

  static clientOrderByToDomain(
    clientOrderBy: UsersOrderBy,
  ): UsersOrderByFields {
    switch (clientOrderBy) {
      case UsersOrderBy.NAME:
        return 'name';
      case UsersOrderBy.CREATED_AT:
        return 'createdAt';
      case UsersOrderBy.UPDATED_AT:
        return 'updatedAt';
    }
  }
}
