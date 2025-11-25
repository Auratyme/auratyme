import { SleepPhase } from '../enums';

export class SleepRecordCreateDto {
  userId: string;
  startTime: string;
  endTime: string;
  phase: (typeof SleepPhase)[keyof typeof SleepPhase];
}
