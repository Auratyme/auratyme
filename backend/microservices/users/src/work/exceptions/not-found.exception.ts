import { WorkException } from './work.exception';

export class WorkNotFoundException extends WorkException {
  constructor(userId: string) {
    super(`Work info for user with id = ${userId} was not found`);
  }
}
