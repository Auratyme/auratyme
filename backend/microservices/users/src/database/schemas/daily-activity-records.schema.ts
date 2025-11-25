import { pgTable, timestamp, integer, uuid } from 'drizzle-orm/pg-core';
import { usersTable } from './users.schema';
import { userId } from './helpers';

export const dailyActivityRecordsTable = pgTable('daily_activity_records', {
  id: uuid().primaryKey().defaultRandom(),
  userId: userId.references(() => usersTable.id),
  date: timestamp().notNull(),
  steps: integer().notNull(),
});
