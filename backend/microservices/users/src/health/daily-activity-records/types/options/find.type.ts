import { FindOptions } from 'common';
import { DbDailyActivityRecord } from '../db';

export type DailyActivityRecordsFindOptions = FindOptions<
  Partial<DbDailyActivityRecord>,
  keyof DbDailyActivityRecord
>;
