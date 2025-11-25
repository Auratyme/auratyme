import { FindOptions } from 'common';
import { DbSleepRecord } from '../db.type';

export type SleepRecordsFindOptions = FindOptions<
  Partial<DbSleepRecord>,
  keyof DbSleepRecord
>;
