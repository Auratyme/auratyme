import { WorkType } from '../enums';

export class WorkResponseDto {
  startTime?: string | null;
  endTime?: string | null;
  commuteTimeMinutes?: number | null;
  type: (typeof WorkType)[keyof typeof WorkType];
}
