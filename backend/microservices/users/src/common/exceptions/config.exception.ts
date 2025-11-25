import { AppException } from './app.exception';

export class ConfigException extends AppException {
  constructor(message: string) {
    super(message, undefined, false);
  }
}
