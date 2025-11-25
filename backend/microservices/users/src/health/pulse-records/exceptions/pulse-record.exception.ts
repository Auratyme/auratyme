import { AppException } from '@app/common/exceptions';

export class PulseRecordException extends AppException {
  constructor(message: string, cause: unknown) {
    super(message, cause, true);
  }
}
