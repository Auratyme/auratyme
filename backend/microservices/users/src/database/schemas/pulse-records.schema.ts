import { pgTable, timestamp, integer, uuid } from 'drizzle-orm/pg-core';
import { usersTable } from './users.schema';
import { userId } from './helpers';

export const pulseRecordsTable = pgTable('pulse_records', {
  id: uuid().primaryKey().defaultRandom(),
  userId: userId.references(() => usersTable.id),
  pulse: integer().notNull(),
  timestamp: timestamp().notNull(),
});
