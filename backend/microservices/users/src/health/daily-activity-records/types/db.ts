import { dailyActivityRecordsTable } from '@app/database/schemas';

export type DbDailyActivityRecord =
  typeof dailyActivityRecordsTable.$inferSelect;
