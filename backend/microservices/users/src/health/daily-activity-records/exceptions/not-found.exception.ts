import { DailyActivityRecordException } from './daily-activity-record.exception';

export class DailyActivityRecordNotFoundException extends DailyActivityRecordException {
  constructor(message: string, cause: unknown) {
    super(message, cause);
  }
}
