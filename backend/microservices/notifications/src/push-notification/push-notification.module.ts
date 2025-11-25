import { Module } from '@nestjs/common';
import { PushNotificationService } from './push-notification.service';
import { PushTokensModule } from '../push-token/push-token.module';

@Module({
  imports: [PushTokensModule],
  providers: [PushNotificationService],
  exports: [PushNotificationService],
})
export class PushNotificationModule {}
