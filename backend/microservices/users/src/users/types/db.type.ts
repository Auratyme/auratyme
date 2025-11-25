import { usersTable } from '@app/database/schemas';

export type DbUser = typeof usersTable.$inferSelect;
