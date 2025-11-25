import { DbSchedule } from '../db.type';

export type SchedulesOrderByFields = Exclude<
  keyof DbSchedule,
  'id' | 'description' | 'userId'
>;
