import { Controller, Logger, UseInterceptors } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { TaskEvent } from './enums';
import { TaskEventPayload } from './types';
import { PushNotification } from '../push-notification/types';
import { PushNotificationService } from '../push-notification/push-notification.service';
import { RmqRequestInterceptor } from '../common/interceptors';

@UseInterceptors(RmqRequestInterceptor)
@Controller()
export class TaskEventController {
  private readonly logger = new Logger(TaskEventController.name);

  constructor(
    private readonly pushNotificationService: PushNotificationService,
  ) {}

  @EventPattern(TaskEvent.DUE)
  async handleDue(@Payload() payload: TaskEventPayload) {
    try {
      const title = `Task ${payload.taskName} expired!`;
      const pushNotification: PushNotification = {
        title,
        sound: 'default',
        priority: 'high',
        interruptionLevel: 'active',
      };

      await this.pushNotificationService.sendPushNotifications(
        pushNotification,
        payload.userId,
      );
    } catch (err) {
      this.logger.error(
        `Failed to handle ${TaskEvent.DUE} event, details: `,
        err,
      );
    }
  }

  @EventPattern(TaskEvent.REPEATED)
  async handleRepeated(@Payload() payload: TaskEventPayload) {
    try {
      const title = `Task ${payload.taskName} repeated!`;
      const pushNotification: PushNotification = {
        title,
        sound: 'default',
        priority: 'high',
        interruptionLevel: 'active',
      };

      await this.pushNotificationService.sendPushNotifications(
        pushNotification,
        payload.userId,
      );
    } catch (err) {
      this.logger.error(
        `Failed to handle ${TaskEvent.REPEATED} event, details: `,
        err,
      );
    }
  }
}
