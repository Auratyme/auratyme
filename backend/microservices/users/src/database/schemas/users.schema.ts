import { UserContraints } from '@app/users/enums';
import { varchar } from 'drizzle-orm/pg-core';
import { pgTable } from 'drizzle-orm/pg-core';
import { createdAt, updatedAt, userId } from './helpers';

export const usersTable = pgTable('users', {
  id: userId.primaryKey(),
  createdAt: createdAt,
  updatedAt: updatedAt,
  name: varchar({ length: UserContraints.MAX_NAME_LENGTH }).notNull(),
});
