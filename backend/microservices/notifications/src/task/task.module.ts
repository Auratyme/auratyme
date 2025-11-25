import { Module } from '@nestjs/common';

import { PushNotificationModule } from '../push-notification/push-notification.module';
import { TaskEventController } from './task-event.controller';

@Module({
  imports: [PushNotificationModule],
  controllers: [TaskEventController],
})
export class TaskModule {}
