import { AppException } from '@app/common/exceptions';

export class MealException extends AppException {
  constructor(message: string) {
    super(message, undefined, true);
  }
}
