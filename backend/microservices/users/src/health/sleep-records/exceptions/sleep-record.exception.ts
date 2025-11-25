import { AppException } from 'common';

export class SleepRecordException extends AppException {
  constructor(message: string, cause: unknown) {
    super(message, cause, true);
  }
}
