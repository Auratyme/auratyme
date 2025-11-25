import { UpdateOptions } from 'common';
import { SchedulesUpdateFields } from '../helpers';

export type ScheduleUpdateOptions = UpdateOptions<
  {
    id: string;
    userId?: string;
  },
  SchedulesUpdateFields
>;
