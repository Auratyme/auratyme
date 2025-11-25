import { AppException } from '@app/common/exceptions';

export class RoutineException extends AppException {
  constructor(message: string) {
    super(message, undefined, true);
  }
}
