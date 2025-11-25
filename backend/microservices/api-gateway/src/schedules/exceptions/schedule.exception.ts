import { AppException } from 'common';

export class ScheduleException extends AppException {
  scheduleId: string;
  constructor(message: string, cause: unknown, scheduleId: string) {
    super(message, cause, true);

    this.scheduleId = scheduleId;
  }
}
