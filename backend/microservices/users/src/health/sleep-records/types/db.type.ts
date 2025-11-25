import { sleepRecordsTable } from '@app/database/schemas';

export type DbSleepRecord = typeof sleepRecordsTable.$inferSelect;
