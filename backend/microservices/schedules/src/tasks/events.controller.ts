import { Controller, Logger, UseInterceptors } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';

import { EventsService } from '../events/events.service';
import { TaskEventPayload, TaskJobPayload } from './types';
import { TaskEvent, TaskStatus } from './enums';
import { TasksService } from './tasks.service';
import { RmqRequestInterceptor } from 'common';

@UseInterceptors(RmqRequestInterceptor)
@Controller()
export class TaskEventsController {
  private readonly logger = new Logger(TaskEventsController.name);

  constructor(
    private readonly eventsService: EventsService<TaskEventPayload>,
    private readonly tasksService: TasksService,
  ) {}

  @EventPattern(TaskEvent.DUE)
  async handleDue(
    @Payload()
    payload: TaskJobPayload,
  ) {
    try {
      const task = await this.tasksService.findOne({
        where: { id: payload.taskId },
      });

      if (
        task.status === TaskStatus.NOT_STARTED ||
        task.status === TaskStatus.IN_PROGRESS
      ) {
        await this.tasksService.update({
          where: { id: task.id, userId: task.userId },
          fields: {
            status: TaskStatus.FAILED,
          },
        });
      }

      this.eventsService.publish(TaskEvent.DUE, {
        task: {
          id: task.id,
          userId: task.userId,
        },
      });
    } catch (err) {
      this.logger.error(
        `Failed to handle ${TaskEvent.DUE} event, details: `,
        err,
      );
    }
  }

  @EventPattern(TaskEvent.REPEATED)
  async handleRepetition(@Payload() payload: TaskJobPayload) {
    try {
      const task = await this.tasksService.findOne({
        where: { id: payload.taskId },
      });

      await this.tasksService.update({
        where: { id: task.id, userId: task.userId },
        fields: {
          status: TaskStatus.NOT_STARTED,
        },
      });

      this.eventsService.publish(TaskEvent.REPEATED, {
        task: {
          id: task.id,
          userId: task.userId,
        },
      });
    } catch (err) {
      this.logger.error(
        `Failed to handle ${TaskEvent.REPEATED} event, details: `,
        err,
      );
    }
  }
}
