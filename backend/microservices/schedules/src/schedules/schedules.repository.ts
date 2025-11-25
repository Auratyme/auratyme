import { Injectable } from '@nestjs/common';
import { and, eq, asc, desc } from 'drizzle-orm';

import { DatabaseException } from 'common';
import { schedulesTable } from '@app/database/schemas';
import { DatabaseService } from '@app/database/database.service';
import {
  DbSchedule,
  ScheduleCreateOptions,
  ScheduleFindOneOptions,
  ScheduleRemoveOptions,
  SchedulesFindOptions,
  ScheduleUpdateOptions,
} from './types';
import { Database } from '../database/types';
import { DatabaseError as PostgresError } from 'pg';
import { PG_FOREIGN_KEY_VIOLATION } from '@drdgvhbh/postgres-error-codes';
import { ForeignKeyViolationException } from 'common';
import { DrizzleError } from 'drizzle-orm';
import { DrizzleQueryError } from 'drizzle-orm';
/**
 * Repository for managing schedules.
 */
@Injectable()
export class SchedulesRepository {
  private readonly db: Database;

  constructor(private readonly databaseService: DatabaseService) {
    this.db = databaseService.getDb();
  }

  /**
   * Finds multiple schedules based on the provided options.
   * @param {SchedulesFindManyOptions} options - The options to filter schedules.
   * @returns {Promise<Schedule[]>} A promise that resolves to an array of schedules.
   * @throws {DatabaseException} If there is an error finding schedules.
   */
  async find(options: SchedulesFindOptions): Promise<DbSchedule[]> {
    const {
      limit = 10,
      orderBy = 'createdAt',
      page = 0,
      sortBy = 'desc',
      where,
    } = options;

    const userId = where?.userId;

    try {
      const result = await this.db
        .select()
        .from(schedulesTable)
        .where(and(userId ? eq(schedulesTable.userId, userId) : undefined))
        .limit(limit)
        .offset(page * limit)
        .orderBy(
          sortBy === 'asc'
            ? asc(schedulesTable[orderBy])
            : desc(schedulesTable[orderBy]),
        );

      return result;
    } catch (err) {
      throw new DatabaseException('Failed to find many schedules', err, true);
    }
  }

  /**
   * Finds a schedule by ID and user ID.
   * @param {string} id - The ID of the schedule.
   * @param {string} userId - The ID of the user.
   * @returns {Promise<Schedule>} A promise that resolves to the schedule.
   * @throws {ScheduleNotFoundException} If the schedule is not found.
   * @throws {DatabaseException} If there is an error finding the schedule.
   */
  async findOne(options: ScheduleFindOneOptions): Promise<DbSchedule | null> {
    const id = options.where.id;
    const userId = options.where.userId;

    try {
      const result = await this.db
        .select()
        .from(schedulesTable)
        .where(
          and(
            eq(schedulesTable.id, id),
            userId ? eq(schedulesTable.userId, userId) : undefined,
          ),
        )
        .limit(1);

      return result.length <= 0 ? null : result[0];
    } catch (err) {
      throw new DatabaseException('Failed to find one schedule', err, true);
    }
  }

  /**
   * Creates a new schedule.
   * @param {CreateScheduleDto} createDto - The new schedule data.
   * @returns {Promise<Schedule>} A promise that resolves to the created schedule.
   * @throws {DatabaseException} If there is an error creating the schedule.
   */
  async create(options: ScheduleCreateOptions): Promise<DbSchedule> {
    try {
      const result = await this.db
        .insert(schedulesTable)
        .values(options)
        .returning();

      return result[0];
    } catch (err) {
      throw new DatabaseException('Failed to create schedule', err, true);
    }
  }

  /**
   * Updates a schedule by ID and user ID.
   * @param {string} id - The ID of the schedule.
   * @param {string} userId - The ID of the user.
   * @param {UpdateScheduleDto} newSchedule - The new schedule data.
   * @returns {Promise<Schedule>} A promise that resolves to the updated schedule.
   * @throws {ScheduleNotFoundException} If the schedule is not found.
   * @throws {DatabaseException} If there is an error updating the schedule.
   */
  async update(options: ScheduleUpdateOptions): Promise<DbSchedule | null> {
    const fields = options.fields;
    const where = options.where;

    try {
      const result = await this.db
        .update(schedulesTable)
        .set({
          name: fields?.name || undefined,
          description: fields?.description,
        })
        .where(
          and(
            eq(schedulesTable.id, where.id),
            where.userId ? eq(schedulesTable.userId, where.userId) : undefined,
          ),
        )
        .returning();

      return result.length <= 0 ? null : result[0];
    } catch (err) {
      throw new DatabaseException('Failed to update one schedule', err, true);
    }
  }

  /**
   * Removes a schedule by ID and user ID.
   * @param {string} id - The ID of the schedule.
   * @param {string} userId - The ID of the user.
   * @returns {Promise<void>} A promise that resolves when the schedule is removed.
   * @throws {ScheduleNotFoundException} If the schedule is not found.
   * @throws {DatabaseException} If there is an error removing the schedule.
   */
  async remove(options: ScheduleRemoveOptions): Promise<DbSchedule | null> {
    const where = options.where;

    try {
      const result = await this.db
        .delete(schedulesTable)
        .where(
          and(
            eq(schedulesTable.id, where.id),
            where.userId ? eq(schedulesTable.userId, where.userId) : undefined,
          ),
        )
        .returning();

      return result.length <= 0 ? null : result[0];
    } catch (err) {
      if (err instanceof DrizzleQueryError) {
        if (err.cause instanceof PostgresError) {
          if (err.cause.code === PG_FOREIGN_KEY_VIOLATION) {
            throw new ForeignKeyViolationException(
              'cannot remove schedule, because it has tasks',
              err,
            );
          }
        }
      }

      throw new DatabaseException('Failed to remove one schedule', err, true);
    }
  }
}
