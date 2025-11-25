import { TaskResponseDto } from './dtos';
import { TaskStatus } from './enums';
import { TaskStatus as ClientTaskStatus, Task as ClientTask } from 'contracts';

export class TasksMapper {
  static clientToResponseDto(clientTask: ClientTask): TaskResponseDto {
    return {
      ...clientTask,
      description:
        clientTask.description?.length === 0 ? null : clientTask.description,
      dueTo: clientTask.dueTo?.length === 0 ? null : clientTask.dueTo,
      repeat: clientTask.repeat?.length === 0 ? null : clientTask.repeat,
      startTime:
        clientTask.startTime?.length === 0 ? null : clientTask.startTime,
      endTime: clientTask.endTime?.length === 0 ? null : clientTask.endTime,
      status: this.clientToDomainStatus(clientTask.status),
    };
  }

  static domainToClientStatus(
    status: (typeof TaskStatus)[keyof typeof TaskStatus],
  ): ClientTaskStatus {
    switch (status) {
      case 'not-started':
        return ClientTaskStatus.NOT_STARTED;
      case 'in-progress':
        return ClientTaskStatus.IN_PROGRESS;
      case 'done':
        return ClientTaskStatus.DONE;
      case 'failed':
        return ClientTaskStatus.FAILED;
    }
  }

  static clientToDomainStatus(
    numericStatus: ClientTaskStatus,
  ): (typeof TaskStatus)[keyof typeof TaskStatus] {
    switch (numericStatus) {
      case ClientTaskStatus.NOT_STARTED:
        return 'not-started';
      case ClientTaskStatus.IN_PROGRESS:
        return 'in-progress';
      case ClientTaskStatus.DONE:
        return 'done';
      case ClientTaskStatus.FAILED:
        return 'failed';
    }
  }
}
