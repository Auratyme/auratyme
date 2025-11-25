import { schedulesTable } from '@/src/database/schemas';

export type DbSchedule = typeof schedulesTable.$inferSelect;
