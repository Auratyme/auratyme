import { tasksTable } from '@/src/database/schemas';

export type DbTask = typeof tasksTable.$inferSelect;
