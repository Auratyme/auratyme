import { pgTable } from 'drizzle-orm/pg-core';
import { usersTable } from './users.schema';
import { userId } from './helpers';

export const preferencesTable = pgTable('preferences', {
  userId: userId.references(() => usersTable.id).primaryKey(),
});
