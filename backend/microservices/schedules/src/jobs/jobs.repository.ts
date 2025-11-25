import { Injectable, Logger } from '@nestjs/common';
import { Database } from '../database/types';
import { DatabaseService } from '../database/database.service';
import { jobsTable } from '../database/schemas/jobs.schema';
import { DbJob } from './types';
import { DatabaseException } from 'common';
import { eq } from 'drizzle-orm';
import { JobType } from './enums';

@Injectable()
export class JobsRepository {
  private readonly logger = new Logger(JobsRepository.name);
  private readonly db: Database;

  constructor(databaseService: DatabaseService) {
    this.db = databaseService.getDb();
  }

  async findOne(id: string): Promise<DbJob | null> {
    try {
      const result = await this.db
        .select()
        .from(jobsTable)
        .where(eq(jobsTable.id, id));

      return result.length <= 0 ? null : result[0];
    } catch (err) {
      throw new DatabaseException('Failed to find one job', err, true);
    }
  }

  /**
   *
   * @param taskId - task id that job belongs to
   * @returns maximum 2 jobs (cron and single, cron or single, empty array)
   */
  async findByTaskId(taskId: string): Promise<DbJob[]> {
    try {
      const result = await this.db
        .select()
        .from(jobsTable)
        .where(eq(jobsTable.taskId, taskId));

      return result;
    } catch (err) {
      throw new DatabaseException('Failed to find job by taskId', err, true);
    }
  }

  async save(
    id: string,
    type: (typeof JobType)[keyof typeof JobType],
    taskId: string,
  ): Promise<DbJob> {
    try {
      const result = await this.db
        .insert(jobsTable)
        .values({
          type,
          id,
          taskId,
        })
        .returning();

      return result[0];
    } catch (err) {
      throw new DatabaseException('Failed to save job', err, true);
    }
  }

  async remove(id: string): Promise<boolean> {
    try {
      const result = await this.db
        .delete(jobsTable)
        .where(eq(jobsTable.id, id));

      return Boolean(result.rowCount);
    } catch (err) {
      throw new DatabaseException('Failed to save job', err, true);
    }
  }
}
