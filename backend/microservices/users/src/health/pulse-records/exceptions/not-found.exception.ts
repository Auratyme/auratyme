import { PulseRecordException } from './pulse-record.exception';

export class PulseRecordNotFoundException extends PulseRecordException {
  constructor(message: string, cause: unknown) {
    super(message, cause);
  }
}
