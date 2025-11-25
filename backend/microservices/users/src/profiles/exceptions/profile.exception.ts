import { AppException } from '@app/common/exceptions';

export class ProfileException extends AppException {
  constructor(message: string) {
    super(message, undefined, true);
  }
}
