import { SleepPhase } from '../enums';

export class SleepRecordResponseDto {
  id: string;
  userId: string;
  startTime: string;
  endTime: string;
  phase: (typeof SleepPhase)[keyof typeof SleepPhase];
}
