import { FindOptions } from 'common';
import { DbRoutine } from '../db.type';

export type RoutinesFindOptions = FindOptions<
  Partial<DbRoutine>,
  keyof DbRoutine
>;
