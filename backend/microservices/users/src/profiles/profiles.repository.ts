import { Injectable } from '@nestjs/common';
import { ProfileCreateDto, ProfileUpdateDto } from './dtos';
import { Database } from '@app/database/types';
import { DatabaseService } from '@app/database/database.service';
import { DbProfile } from './types/db.type';
import { profilesTable } from '@app/database/schemas';
import { eq, asc, desc } from 'drizzle-orm';
import { ProfilesFindOptions } from './types/options/find.type';

@Injectable()
export class ProfilesRepository {
  private readonly db: Database;

  constructor(readonly databaseService: DatabaseService) {
    this.db = databaseService.getDb();
  }

  async find(options: ProfilesFindOptions): Promise<DbProfile[]> {
    const limit = options.limit || 100;
    const page = options.page || 0;
    const sortBy = options.sortBy || 'desc';
    const orderBy = options.orderBy || 'birthDate';
    const userId = options.where?.userId;

    const result = await this.db
      .select()
      .from(profilesTable)
      .limit(limit)
      .offset(limit * page)
      .where(userId ? eq(profilesTable.userId, userId) : undefined)
      .orderBy(
        sortBy === 'asc'
          ? asc(profilesTable[orderBy])
          : desc(profilesTable[orderBy]),
      );

    return result;
  }

  async findOne(userId: string): Promise<DbProfile | null> {
    const result = await this.db
      .select()
      .from(profilesTable)
      .where(eq(profilesTable.userId, userId));

    return result.length <= 0 ? null : result[0];
  }

  async findForUser(userId: string): Promise<DbProfile | null> {
    const result = await this.db
      .select()
      .from(profilesTable)
      .where(eq(profilesTable.userId, userId));

    return result.length <= 0 ? null : result[0];
  }

  async create(createDto: ProfileCreateDto): Promise<DbProfile> {
    const result = await this.db
      .insert(profilesTable)
      .values({
        userId: createDto.userId,
        birthDate: createDto.birthDate ? new Date(createDto.birthDate) : null,
        chronotypeMEQ: createDto.chronotypeMEQ || null,
      })
      .returning();

    return result[0];
  }

  async update(updateDto: ProfileUpdateDto): Promise<DbProfile | null> {
    const fields = updateDto.fields;

    const birthDate = fields?.birthDate
      ? new Date(fields.birthDate)
      : fields?.birthDate === null
        ? null
        : undefined;

    const result = await this.db
      .update(profilesTable)
      .set({
        birthDate,
        chronotypeMEQ: fields?.chronotypeMEQ,
      })
      .where(eq(profilesTable.userId, updateDto.userId))
      .returning();

    return result.length <= 0 ? null : result[0];
  }

  async remove(userId: string): Promise<DbProfile | null> {
    const result = await this.db
      .delete(profilesTable)
      .where(eq(profilesTable.userId, userId))
      .returning();

    return result.length <= 0 ? null : result[0];
  }
}
