import { ProfileException } from './profile.exception';

export class ProfileNotFoundException extends ProfileException {
  constructor(userId: string) {
    super(`User with id = ${userId} was not found`);
  }
}
