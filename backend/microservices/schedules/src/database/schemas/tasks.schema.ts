import {
  pgTable,
  uuid,
  varchar,
  timestamp,
  pgEnum,
  integer,
  boolean,
  time,
} from 'drizzle-orm/pg-core';

import { schedulesTable } from './schedules.schema';
import { createdAt, updatedAt, id } from './helpers';
import { TaskStatus, TaskConstraint } from '@app/tasks/enums';

export const taskStatusEnum = pgEnum('task_status', [
  TaskStatus.DONE,
  TaskStatus.FAILED,
  TaskStatus.IN_PROGRESS,
  TaskStatus.NOT_STARTED,
]);

export const tasksTable = pgTable('tasks', {
  id,
  name: varchar({ length: TaskConstraint.MAX_NAME_LENGTH }).notNull(),
  description: varchar({ length: TaskConstraint.MAX_DESCRIPTION_LENGTH }),
  status: taskStatusEnum().notNull().default(TaskStatus.NOT_STARTED),
  dueTo: timestamp(),
  repeat: varchar({ length: TaskConstraint.MAX_REPEAT_LENGTH }),
  userId: varchar({ length: TaskConstraint.MAX_USER_ID_LENGTH }).notNull(),
  priority: integer().notNull().default(0),
  fixed: boolean().notNull().default(false),
  startTime: time(),
  endTime: time(),
  createdAt,
  updatedAt,
  scheduleId: uuid()
    .notNull()
    .references(() => schedulesTable.id),
});
