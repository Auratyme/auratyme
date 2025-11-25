import { FindOneOptions } from 'common';
import { DbTask } from '../db.type';

export type TaskFindOneOptions = FindOneOptions<{
  id: string;
  userId?: string;
}>;
