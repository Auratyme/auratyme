import { AppException } from 'common';

export class JobException extends AppException {
  jobId: string;
  constructor(message: string, cause: unknown, jobId: string) {
    super(message, cause, true);

    this.jobId = jobId;
  }
}
