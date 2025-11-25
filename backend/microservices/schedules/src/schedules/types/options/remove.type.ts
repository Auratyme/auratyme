import { RemoveOptions } from 'common';

export type ScheduleRemoveOptions = RemoveOptions<{
  id: string;
  userId?: string;
}>;
