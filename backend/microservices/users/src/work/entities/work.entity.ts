import { WorkType } from '@app/work/enums';

export class Work {
  userId: string;
  startTime: string | null;
  endTime: string | null;
  commuteTimeMinutes: number | null;
  type: (typeof WorkType)[keyof typeof WorkType];
}
