import { schedulesTable } from '@app/database/schemas';

export type ScheduleCreateOptions = Omit<
  typeof schedulesTable.$inferInsert,
  'createdAt' | 'updatedAt' | 'id'
>;
