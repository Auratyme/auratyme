import { AppException } from 'common';

export class TaskException extends AppException {
  taskId: string;
  constructor(taskId: string, message: string, cause: unknown) {
    super(message, cause, true);

    this.taskId = taskId;
  }
}
