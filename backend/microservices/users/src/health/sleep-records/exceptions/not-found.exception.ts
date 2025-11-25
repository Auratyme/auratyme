import { SleepRecordException } from './sleep-record.exception';

export class SleepRecordNotFoundException extends SleepRecordException {
  constructor(message: string, cause: unknown) {
    super(message, cause);
  }
}
