import { profilesTable } from '@app/database/schemas/profiles.schema';

export type DbProfile = typeof profilesTable.$inferSelect;
