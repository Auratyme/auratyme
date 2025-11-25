import { date, pgTable, integer } from 'drizzle-orm/pg-core';
import { usersTable } from './users.schema';
import { userId } from './helpers';

export const profilesTable = pgTable('profiles', {
  userId: userId.references(() => usersTable.id).primaryKey(),
  birthDate: date({ mode: 'date' }),
  chronotypeMEQ: integer(),
});
