import { usersTable } from '@app/database/schemas';

export type UserCreateOptions = typeof usersTable.$inferInsert;
