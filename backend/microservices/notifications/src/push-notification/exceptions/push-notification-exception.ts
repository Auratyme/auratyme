import { AppException } from '@/src/common/exceptions';

export class PushNotificationException extends AppException {
  constructor(message: string, cause: unknown) {
    super(message, cause, true);
  }
}
