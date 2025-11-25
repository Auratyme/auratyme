import { Module } from '@nestjs/common';
import { PushTokensService } from './push-tokens.service';
import { PushTokensController } from './push-tokens.controller';

@Module({
  providers: [PushTokensService],
  controllers: [PushTokensController]
})
export class PushTokensModule {}
