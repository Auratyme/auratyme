import { DbTask } from '../db.type';

export type TasksUpdateFields = Partial<
  Omit<DbTask, 'createdAt' | 'updatedAt' | 'id' | 'userId' | 'dueTo'> & {
    dueTo?: Date | null;
  }
>;
