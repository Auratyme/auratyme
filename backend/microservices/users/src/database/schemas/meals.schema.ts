import { pgTable, uuid, varchar, time, integer } from 'drizzle-orm/pg-core';
import { usersTable } from './users.schema';
import { userId } from './helpers';

export const mealsTable = pgTable('meals', {
  id: uuid().primaryKey().defaultRandom(),
  name: varchar({ length: 255 }).notNull(),
  userId: userId.references(() => usersTable.id),
  startTime: time({ precision: 0 }),
  durationMinutes: integer(),
});
