import { DatabaseService } from '@app/database/database.service';
import { Database } from '@app/database/types';
import { Injectable } from '@nestjs/common';
import { DbPulseRecord, PulseRecordsFindOptions } from './types';
import { pulseRecordsTable } from '@app/database/schemas/pulse-records.schema';
import { PulseRecordCreateDto } from './dtos';
import { asc, desc, eq } from 'drizzle-orm';

@Injectable()
export class PulseRecordsRepository {
  private readonly db: Database;

  constructor(readonly dbService: DatabaseService) {
    this.db = dbService.getDb();
  }

  async find(options: PulseRecordsFindOptions): Promise<DbPulseRecord[]> {
    const limit = options.limit || 100;
    const page = options.page || 0;
    const sortBy = options.sortBy || 'desc';
    const orderBy = options.orderBy || 'timestamp';
    const userId = options.where?.userId;

    const result = await this.db
      .select()
      .from(pulseRecordsTable)
      .where(userId ? eq(pulseRecordsTable.userId, userId) : undefined)
      .limit(limit)
      .offset(page * limit)
      .orderBy(
        sortBy === 'asc'
          ? asc(pulseRecordsTable[orderBy])
          : desc(pulseRecordsTable[orderBy]),
      );

    return result;
  }

  async findOne(id: string): Promise<DbPulseRecord | null> {
    const result = await this.db
      .select()
      .from(pulseRecordsTable)
      .where(eq(pulseRecordsTable.id, id));

    return result.length > 0 ? result[0] : null;
  }

  async create(createDto: PulseRecordCreateDto): Promise<DbPulseRecord> {
    const result = await this.db
      .insert(pulseRecordsTable)
      .values({ ...createDto, timestamp: new Date(createDto.timestamp) })
      .returning();

    return result[0];
  }

  async remove(id: string): Promise<DbPulseRecord | null> {
    const result = await this.db
      .delete(pulseRecordsTable)
      .where(eq(pulseRecordsTable.id, id))
      .returning();

    return result.length > 0 ? result[0] : null;
  }
}
