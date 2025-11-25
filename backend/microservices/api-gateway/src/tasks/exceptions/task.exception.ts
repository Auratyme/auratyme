import { AppException } from 'common';

export class TaskException extends AppException {
  taskId: string;
  constructor(message: string, cause: unknown, taskId: string) {
    super(message, cause, true);

    this.taskId = taskId;
  }
}
