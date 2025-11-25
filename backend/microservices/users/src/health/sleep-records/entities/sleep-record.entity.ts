import { SleepPhase } from '../enums';

export class SleepRecord {
  id: string;
  userId: string;
  startTime: string;
  endTime: string;
  phase: (typeof SleepPhase)[keyof typeof SleepPhase];
}
