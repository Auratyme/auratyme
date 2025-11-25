import { pgTable, uuid, timestamp } from 'drizzle-orm/pg-core';
import { usersTable } from './users.schema';
import { pgEnum } from 'drizzle-orm/pg-core';
import { SleepPhase } from '@app/health/sleep-records/enums';
import { userId } from './helpers';

export const sleepPhaseEnum = pgEnum('sleep_phase', [
  SleepPhase.DEEP,
  SleepPhase.LIGHT,
  SleepPhase.REM,
  SleepPhase.STANDBY,
]);

export const sleepRecordsTable = pgTable('sleep_records', {
  id: uuid().primaryKey().defaultRandom(),
  userId: userId.references(() => usersTable.id),
  startTime: timestamp().notNull(),
  endTime: timestamp().notNull(),
  phase: sleepPhaseEnum().notNull(),
});
