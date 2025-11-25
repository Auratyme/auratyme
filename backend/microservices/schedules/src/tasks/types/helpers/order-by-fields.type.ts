import { DbTask } from '../db.type';

export type TasksOrderByFields = Extract<
  keyof DbTask,
  'createdAt' | 'updatedAt' | 'status' | 'name' | 'dueTo'
>;
