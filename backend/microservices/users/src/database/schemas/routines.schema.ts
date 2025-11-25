import { pgTable, varchar, integer, uuid } from 'drizzle-orm/pg-core';
import { UserContraints } from '@app/users/enums';
import { usersTable } from './users.schema';
import { userId } from './helpers';

export const routinesTable = pgTable('routines', {
  id: uuid().primaryKey().defaultRandom(),
  userId: userId.references(() => usersTable.id),
  name: varchar({ length: 255 }).notNull(),
  durationMinutes: integer(),
});
