import { FindOptions } from 'common';
import { DbPulseRecord } from '../db-pulse-record';

export type PulseRecordsFindOptions = FindOptions<
  Partial<DbPulseRecord>,
  keyof DbPulseRecord
>;
