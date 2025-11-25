import { WorkType } from '../enums';

export class WorkUpdateDto {
  userId: string;
  fields?: {
    startTime?: string | null;
    endTime?: string | null;
    commuteTimeMinutes?: number | null;
    type?: (typeof WorkType)[keyof typeof WorkType];
  };
}
