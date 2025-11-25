import { Injectable } from '@nestjs/common';
import { Database } from '@app/database/types';
import { DatabaseService } from '@app/database/database.service';
import { DbUser } from './types/db.type';
import { usersTable } from '@app/database/schemas';
import { eq, asc, desc } from 'drizzle-orm';
import { UsersFindOptions } from './types/options/find.type';
import {
  UserCreateOptions,
  UserFindOneOptions,
  UserRemoveOptions,
  UserUpdateOptions,
} from './types/options';

@Injectable()
export class UsersRepository {
  private readonly db: Database;

  constructor(readonly databaseService: DatabaseService) {
    this.db = databaseService.getDb();
  }

  async find(options?: UsersFindOptions): Promise<DbUser[]> {
    const limit = options?.limit || 100;
    const page = options?.page || 0;
    const sortBy = options?.sortBy || 'desc';
    const orderBy = options?.orderBy || 'createdAt';

    const result = await this.db
      .select()
      .from(usersTable)
      .limit(limit)
      .offset(limit * page)
      .orderBy(
        sortBy === 'asc' ? asc(usersTable[orderBy]) : desc(usersTable[orderBy]),
      );

    return result;
  }

  async findOne(options: UserFindOneOptions): Promise<DbUser | null> {
    const result = await this.db
      .select()
      .from(usersTable)
      .where(eq(usersTable.id, options.where.id));

    return result.length <= 0 ? null : result[0];
  }

  async create(options: UserCreateOptions): Promise<DbUser> {
    const result = await this.db.insert(usersTable).values(options).returning();

    return result[0];
  }

  async update(options: UserUpdateOptions): Promise<DbUser | null> {
    const result = await this.db
      .update(usersTable)
      .set(options.fields || {})
      .where(eq(usersTable.id, options.where.id))
      .returning();

    return result.length <= 0 ? null : result[0];
  }

  async remove(options: UserRemoveOptions): Promise<DbUser | null> {
    const result = await this.db
      .delete(usersTable)
      .where(eq(usersTable.id, options.where.id))
      .returning();

    return result.length <= 0 ? null : result[0];
  }
}
