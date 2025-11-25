import { AppException } from '@app/common/exceptions';

export class UserException extends AppException {
  constructor(message: string, userId: string) {
    super(message, undefined, true);
  }
}
