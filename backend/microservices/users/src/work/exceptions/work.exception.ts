import { AppException } from '@app/common/exceptions';

export class WorkException extends AppException {
  constructor(message: string) {
    super(message, undefined, true);
  }
}
