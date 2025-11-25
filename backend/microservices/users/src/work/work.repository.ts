import { Injectable } from '@nestjs/common';
import { WorkCreateDto, WorkUpdateDto } from './dtos';
import { Database } from '@app/database/types';
import { DatabaseService } from '@app/database/database.service';
import { DbWork } from './types/db.type';
import { workTable } from '@app/database/schemas';
import { eq } from 'drizzle-orm';

@Injectable()
export class WorkRepository {
  private readonly db: Database;

  constructor(readonly databaseService: DatabaseService) {
    this.db = databaseService.getDb();
  }

  async findForUser(userId: string): Promise<DbWork | null> {
    const result = await this.db
      .select()
      .from(workTable)
      .where(userId ? eq(workTable.userId, userId) : undefined);

    return result.length <= 0 ? null : result[0];
  }

  async create(createDto: WorkCreateDto): Promise<DbWork> {
    const result = await this.db
      .insert(workTable)
      .values(createDto)
      .returning();

    return result[0];
  }

  async update(updateDto: WorkUpdateDto): Promise<DbWork | null> {
    const fields = updateDto.fields || {};

    const result = await this.db
      .update(workTable)
      .set(fields)
      .where(eq(workTable.userId, updateDto.userId))
      .returning();

    return result.length <= 0 ? null : result[0];
  }

  async remove(userId: string): Promise<DbWork | null> {
    const result = await this.db
      .delete(workTable)
      .where(eq(workTable.userId, userId))
      .returning();

    return result.length <= 0 ? null : result[0];
  }
}
