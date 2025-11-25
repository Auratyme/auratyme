import { UserException } from './user.exception';

export class UserNotFoundException extends UserException {
  constructor(userId: string) {
    super(`User with id = ${userId} was not found`, userId);
  }
}
