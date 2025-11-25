import { pgTable } from 'drizzle-orm/pg-core';
import { pgEnum } from 'drizzle-orm/pg-core';

import { uuid } from 'drizzle-orm/pg-core';
import { tasksTable } from './tasks.schema';
import { varchar } from 'drizzle-orm/pg-core';
import { JobType } from '@app/jobs/enums';

export const jobTypeEnum = pgEnum('job_type', [JobType.CRON, JobType.SINGLE]);

export const jobsTable = pgTable('jobs', {
  id: varchar({ length: 255 }).notNull().primaryKey(),
  type: jobTypeEnum().notNull(),
  taskId: uuid()
    .notNull()
    .references(() => tasksTable.id),
});
