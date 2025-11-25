import { workTable } from '@app/database/schemas';

export type DbWork = typeof workTable.$inferSelect;
