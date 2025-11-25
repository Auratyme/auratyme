import { FindOptions } from 'common';

import { SchedulesOrderByFields } from '../helpers';

export type SchedulesFindOptions = FindOptions<
  {
    userId?: string;
  },
  SchedulesOrderByFields
>;
