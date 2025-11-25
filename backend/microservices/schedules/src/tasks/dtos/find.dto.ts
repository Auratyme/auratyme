import { Task } from '../entities';
import { DateTimeFilter } from '@app/common/types';
import { TaskStatus } from '../enums';
import { TasksOrderByFields } from '../types/helpers';

type Status = (typeof TaskStatus)[keyof typeof TaskStatus];

export class TasksFindDto {
  options?: {
    limit?: number;
    page?: number;
    orderBy?: TasksOrderByFields;
    sortBy?: 'asc' | 'desc';
  };
  where?: Partial<
    Omit<Task, 'createdAt' | 'updatedAt' | 'dueTo' | 'status'> & {
      dueTo?: DateTimeFilter;
      createdAt?: DateTimeFilter;
      updatedAt?: DateTimeFilter;
      status?: Status | Status[];
    }
  >;
}
