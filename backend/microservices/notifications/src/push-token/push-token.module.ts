import { Module } from '@nestjs/common';
import { PushTokenController } from './push-token.controller';
import { PushTokenRepository } from './push-token.repository';
import { PushTokenService } from './push-token.service';
import { AuthModule } from '../auth/auth.module';
import { DatabaseModule } from '../database/database.module';

@Module({
  imports: [AuthModule, DatabaseModule],
  controllers: [PushTokenController],
  providers: [PushTokenRepository, PushTokenService],
  exports: [PushTokenService],
})
export class PushTokensModule {}
