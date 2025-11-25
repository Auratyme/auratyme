import { DbSchedule } from '../db.type';

export type SchedulesUpdateFields = Partial<
  Omit<DbSchedule, 'id' | 'userId' | 'createdAt' | 'updatedAt'>
>;
