import { SchedulesOrderByFields } from '../types/helpers';

export class SchedulesFindDto {
  where?: {
    userId?: string;
  };
  options?: {
    limit?: number;
    page?: number;
    sortBy?: 'asc' | 'desc';
    orderBy?: SchedulesOrderByFields;
  };
}
