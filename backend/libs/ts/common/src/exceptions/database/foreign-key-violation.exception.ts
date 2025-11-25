import { DatabaseException } from './database.exception.js';

export class ForeignKeyViolationException extends DatabaseException {
  constructor(message: string, cause: unknown) {
    super(`Foreign key violation: ${message}`, cause, true);
  }
}
