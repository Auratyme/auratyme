import { Injectable } from '@nestjs/common';
import { RoutineCreateDto, RoutineUpdateDto } from './dtos';
import { Database } from '@app/database/types';
import { DatabaseService } from '@app/database/database.service';
import { DbRoutine } from './types/db.type';
import { routinesTable } from '@app/database/schemas';
import { eq, asc, desc } from 'drizzle-orm';
import { RoutinesFindOptions } from './types/options/find.type';

@Injectable()
export class RoutinesRepository {
  private readonly db: Database;

  constructor(readonly databaseService: DatabaseService) {
    this.db = databaseService.getDb();
  }

  async find(options: RoutinesFindOptions): Promise<DbRoutine[]> {
    const limit = options.limit || 100;
    const page = options.page || 0;
    const sortBy = options.sortBy || 'desc';
    const orderBy = options.orderBy || 'durationMinutes';
    const id = options.where?.id;

    const result = await this.db
      .select()
      .from(routinesTable)
      .limit(limit)
      .offset(limit * page)
      .where(id ? eq(routinesTable.id, id) : undefined)
      .orderBy(
        sortBy === 'asc'
          ? asc(routinesTable[orderBy])
          : desc(routinesTable[orderBy]),
      );

    return result;
  }

  async findOne(id: string): Promise<DbRoutine | null> {
    const result = await this.db
      .select()
      .from(routinesTable)
      .where(eq(routinesTable.id, id));

    return result.length <= 0 ? null : result[0];
  }

  async create(createDto: RoutineCreateDto): Promise<DbRoutine> {
    const result = await this.db
      .insert(routinesTable)
      .values(createDto)
      .returning();

    return result[0];
  }

  async update(updateDto: RoutineUpdateDto): Promise<DbRoutine | null> {
    const result = await this.db
      .update(routinesTable)
      .set(updateDto.fields || {})
      .where(eq(routinesTable.id, updateDto.id))
      .returning();

    return result.length <= 0 ? null : result[0];
  }

  async remove(id: string): Promise<DbRoutine | null> {
    const result = await this.db
      .delete(routinesTable)
      .where(eq(routinesTable.id, id))
      .returning();

    return result.length <= 0 ? null : result[0];
  }
}
