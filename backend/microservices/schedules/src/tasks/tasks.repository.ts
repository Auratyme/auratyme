import { Injectable } from '@nestjs/common';
import { eq, and, asc, desc, gte, lte, inArray, SQL } from 'drizzle-orm';

import { DatabaseException } from 'common';
import { DateTimeFilter } from '@app/common/types';
import { tasksTable } from '@app/database/schemas';
import { DatabaseService } from '@app/database/database.service';
import {
  DbTask,
  TaskCreateOptions,
  TaskFindOneOptions,
  TaskRemoveOptions,
  TasksFindOptions,
  TaskUpdateOptions,
} from './types';
import { Database } from '../database/types';
import { TaskStatus } from './enums';

type Status = (typeof TaskStatus)[keyof typeof TaskStatus];

function getDefaultStartDateString(): string {
  const defaultStartDate = new Date();

  defaultStartDate.setHours(0);
  defaultStartDate.setMinutes(0);
  defaultStartDate.setSeconds(0);
  defaultStartDate.setMilliseconds(0);

  return defaultStartDate.toISOString();
}

function getDefaultEndDateString(): string {
  const defaultEndDate = new Date();

  defaultEndDate.setHours(23);
  defaultEndDate.setMinutes(59);
  defaultEndDate.setSeconds(59);
  defaultEndDate.setMilliseconds(999);
  defaultEndDate.setDate(defaultEndDate.getDate() + 7);

  return defaultEndDate.toISOString();
}

function getStatusFilter(status?: Status | Status[]) {
  let filter: SQL | undefined = undefined;

  if (status) {
    if (Array.isArray(status)) {
      filter = inArray(tasksTable.status, status);
    } else {
      filter = eq(tasksTable.status, status);
    }
  }

  return filter;
}

function getTimestampFilter(
  column: 'createdAt' | 'updatedAt' | 'dueTo',
  value?: DateTimeFilter,
) {
  const defaultStartDate = new Date(getDefaultStartDateString());
  const defaultEndDate = new Date(getDefaultEndDateString());

  let filter: SQL | undefined = undefined;

  if (value) {
    if (typeof value === 'string') {
      filter = eq(tasksTable[column], new Date(value));
    } else {
      filter = and(
        gte(
          tasksTable[column],
          value.start ? new Date(value.start) : defaultStartDate,
        ),
        lte(
          tasksTable[column],
          value.end ? new Date(value.end) : defaultEndDate,
        ),
      );
    }
  }

  return filter;
}

/**
 * Repository for managing tasks.
 */
@Injectable({})
export class TasksRepository {
  private readonly db: Database;

  constructor(private readonly databaseService: DatabaseService) {
    this.db = databaseService.getDb();
  }

  async find(options: TasksFindOptions): Promise<DbTask[]> {
    const {
      limit = 100,
      page = 0,
      orderBy = 'createdAt',
      sortBy = 'desc',
      where,
    } = options;

    const name = where?.name;
    const id = where?.id;
    const userId = where?.userId;
    const status = where?.status;
    const dueTo = where?.dueTo;
    const repeat = where?.repeat;
    const createdAt = where?.createdAt;
    const updatedAt = where?.updatedAt;
    const scheduleId = where?.scheduleId;

    const dueToFilter = getTimestampFilter('dueTo', dueTo);
    const createdAtFilter = getTimestampFilter('createdAt', createdAt);
    const updatedAtFilter = getTimestampFilter('updatedAt', updatedAt);
    const statusFilter = getStatusFilter(status);

    try {
      const tasks = await this.db
        .select()
        .from(tasksTable)
        .where(
          and(
            name ? eq(tasksTable.name, name) : undefined,
            id ? eq(tasksTable.id, id) : undefined,
            userId ? eq(tasksTable.userId, userId) : undefined,
            statusFilter,
            dueToFilter,
            repeat ? eq(tasksTable.repeat, repeat) : undefined,
            scheduleId ? eq(tasksTable.scheduleId, scheduleId) : undefined,
            createdAtFilter,
            updatedAtFilter,
          ),
        )
        .limit(limit)
        .offset(page * limit)
        .orderBy(
          sortBy === 'asc'
            ? asc(tasksTable[orderBy])
            : desc(tasksTable[orderBy]),
        );

      return tasks;
    } catch (err) {
      throw new DatabaseException('Failed to find tasks', err, true);
    }
  }

  /**
   * Finds a task by ID and user ID.
   * @param {string} id - The ID of the task.
   * @param {string} userId - The ID of the user.
   * @returns {Promise<Task>} A promise that resolves to the task.
   * @throws {TaskNotFoundException} If the task is not found.
   * @throws {DatabaseException} If there is an error finding the task.
   */
  async findOne(options: TaskFindOneOptions): Promise<DbTask | null> {
    try {
      const result = await this.db
        .select()
        .from(tasksTable)
        .where(
          and(
            eq(tasksTable.id, options.where.id),
            options.where.userId
              ? eq(tasksTable.userId, options.where.userId)
              : undefined,
          ),
        )
        .limit(1);

      return result.length <= 0 ? null : result[0];
    } catch (err) {
      throw new DatabaseException('Failed to find task', err, true);
    }
  }

  /**
   * Creates a new task.
   * @param {CreateTaskDto} newTask - The new task data.
   * @returns {Promise<Task>} A promise that resolves to the created task.
   * @throws {DatabaseException} If there is an error creating the task.
   */
  async create(options: TaskCreateOptions): Promise<DbTask> {
    try {
      const result = await this.db
        .insert(tasksTable)
        .values(options)
        .returning();

      return result[0];
    } catch (err) {
      throw new DatabaseException('Failed to create task', err, true);
    }
  }

  /**
   * Updates a task by ID and user ID.
   * @param {string} id - The ID of the task.
   * @param {string} userId - The ID of the user.
   * @param {UpdateTaskDto} newTask - The new task data.
   * @returns {Promise<Task>} A promise that resolves to the updated task.
   * @throws {DatabaseException} If there is an error updating the task.
   */
  async update(options: TaskUpdateOptions): Promise<DbTask | null> {
    try {
      const result = await this.db
        .update(tasksTable)
        .set(options.fields || {})
        .where(
          and(
            eq(tasksTable.id, options.where.id),
            options.where.userId
              ? eq(tasksTable.userId, options.where.userId)
              : undefined,
          ),
        )
        .returning();

      return result.length <= 0 ? null : result[0];
    } catch (err) {
      throw new DatabaseException('Failed to update one task', err, true);
    }
  }

  /**
   * Removes a task by ID and user ID.
   * @param {string} id - The ID of the task.
   * @param {string} userId - The ID of the user.
   * @returns {Promise<void>} A promise that resolves when the task is removed.
   * @throws {TaskNotFoundException} If the task is not found.
   * @throws {DatabaseException} If there is an error removing the task.
   */
  async remove(options: TaskRemoveOptions): Promise<DbTask | null> {
    try {
      const result = await this.db
        .delete(tasksTable)
        .where(
          and(
            eq(tasksTable.id, options.where.id),
            options.where.userId
              ? eq(tasksTable.userId, options.where.userId)
              : undefined,
          ),
        )
        .returning();

      return result.length <= 0 ? null : result[0];
    } catch (err) {
      throw new DatabaseException('Failed to remove one task', err, true);
    }
  }
}
