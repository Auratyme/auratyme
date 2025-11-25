import { DatabaseService } from '@app/database/database.service';
import { Database } from '@app/database/types';
import { Injectable } from '@nestjs/common';
import { SleepRecordsFindOptions, DbSleepRecord } from './types';
import { SleepRecordCreateDto } from './dtos';
import { sleepRecordsTable } from '@app/database/schemas';
import { eq, asc, desc } from 'drizzle-orm';

@Injectable()
export class SleepRecordsRepository {
  private readonly db: Database;

  constructor(readonly dbService: DatabaseService) {
    this.db = dbService.getDb();
  }

  async find(options: SleepRecordsFindOptions): Promise<DbSleepRecord[]> {
    const limit = options.limit || 100;
    const page = options.page || 0;
    const sortBy = options.sortBy || 'desc';
    const orderBy = options.orderBy || 'startTime';
    const userId = options.where?.userId;

    const result = await this.db
      .select()
      .from(sleepRecordsTable)
      .where(userId ? eq(sleepRecordsTable.userId, userId) : undefined)
      .limit(limit)
      .offset(page * limit)
      .orderBy(
        sortBy === 'asc'
          ? asc(sleepRecordsTable[orderBy])
          : desc(sleepRecordsTable[orderBy]),
      );

    return result;
  }

  async findOne(id: string): Promise<DbSleepRecord | null> {
    const result = await this.db
      .select()
      .from(sleepRecordsTable)
      .where(eq(sleepRecordsTable.id, id));

    return result.length > 0 ? result[0] : null;
  }

  async create(createDto: SleepRecordCreateDto): Promise<DbSleepRecord> {
    const result = await this.db
      .insert(sleepRecordsTable)
      .values({
        ...createDto,
        startTime: new Date(createDto.startTime),
        endTime: new Date(createDto.endTime),
      })
      .returning();

    return result[0];
  }

  async remove(id: string): Promise<DbSleepRecord | null> {
    const result = await this.db
      .delete(sleepRecordsTable)
      .where(eq(sleepRecordsTable.id, id))
      .returning();

    return result.length > 0 ? result[0] : null;
  }
}
