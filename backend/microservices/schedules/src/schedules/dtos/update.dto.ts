import { SchedulesUpdateFields } from '../types/helpers';

export class ScheduleUpdateDto {
  where: {
    id: string;
    userId?: string;
  };
  fields?: SchedulesUpdateFields;
}
