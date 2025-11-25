import { DatabaseService } from '@app/database/database.service';
import { Database } from '@app/database/types';
import { Injectable } from '@nestjs/common';
import {
  DailyActivityRecordsFindOptions,
  DbDailyActivityRecord,
} from './types';
import { DailyActivityRecordCreateDto } from './dtos';
import { dailyActivityRecordsTable } from '@app/database/schemas';
import { eq, asc, desc } from 'drizzle-orm';

@Injectable()
export class DailyActivityRecordsRepository {
  private readonly db: Database;

  constructor(readonly dbService: DatabaseService) {
    this.db = dbService.getDb();
  }

  async find(
    options: DailyActivityRecordsFindOptions,
  ): Promise<DbDailyActivityRecord[]> {
    const limit = options.limit || 100;
    const page = options.page || 0;
    const sortBy = options.sortBy || 'desc';
    const orderBy = options.orderBy || 'date';
    const userId = options.where?.userId;

    const result = await this.db
      .select()
      .from(dailyActivityRecordsTable)
      .where(userId ? eq(dailyActivityRecordsTable.userId, userId) : undefined)
      .limit(limit)
      .offset(page * limit)
      .orderBy(
        sortBy === 'asc'
          ? asc(dailyActivityRecordsTable[orderBy])
          : desc(dailyActivityRecordsTable[orderBy]),
      );

    return result;
  }

  async findOne(id: string): Promise<DbDailyActivityRecord | null> {
    const result = await this.db
      .select()
      .from(dailyActivityRecordsTable)
      .where(eq(dailyActivityRecordsTable.id, id));

    return result.length > 0 ? result[0] : null;
  }

  async create(
    createDto: DailyActivityRecordCreateDto,
  ): Promise<DbDailyActivityRecord> {
    const result = await this.db
      .insert(dailyActivityRecordsTable)
      .values({ ...createDto, date: new Date(createDto.date) })
      .returning();

    return result[0];
  }

  async remove(id: string): Promise<DbDailyActivityRecord | null> {
    const result = await this.db
      .delete(dailyActivityRecordsTable)
      .where(eq(dailyActivityRecordsTable.id, id))
      .returning();

    return result.length > 0 ? result[0] : null;
  }
}
