import { UpdateOptions } from 'common';
import { DbTask } from '../db.type';
import { TasksUpdateFields } from '../helpers';

export type TaskUpdateOptions = UpdateOptions<
  {
    id: string;
    userId?: string;
  },
  TasksUpdateFields
>;
