import { FindOneOptions } from 'common';

export type ScheduleFindOneOptions = FindOneOptions<{
  id: string;
  userId?: string;
}>;
