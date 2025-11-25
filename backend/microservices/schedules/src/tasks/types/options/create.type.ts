import { tasksTable } from '@/src/database/schemas';

export type TaskCreateOptions = Omit<
  typeof tasksTable.$inferInsert,
  'createdAt' | 'updatedAt' | 'id'
>;
