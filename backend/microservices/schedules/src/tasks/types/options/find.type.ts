import { FindOptions } from 'common';
import { TaskStatus } from '@app/tasks/enums';
import { Task } from '../../entities';
import { DateTimeFilter } from '@app/common/types';
import { TasksOrderByFields } from '../helpers';

type Status = (typeof TaskStatus)[keyof typeof TaskStatus];

export type TasksFindOptions = FindOptions<
  Partial<
    Omit<Task, 'createdAt' | 'updatedAt' | 'dueTo' | 'status'> & {
      dueTo?: DateTimeFilter;
      createdAt?: DateTimeFilter;
      updatedAt?: DateTimeFilter;
      status?: Status | Status[];
    }
  >,
  TasksOrderByFields
>;
