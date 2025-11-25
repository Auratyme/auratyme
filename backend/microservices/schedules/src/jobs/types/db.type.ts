import { jobsTable } from '@/src/database/schemas/jobs.schema';

export type DbJob = typeof jobsTable.$inferSelect;
