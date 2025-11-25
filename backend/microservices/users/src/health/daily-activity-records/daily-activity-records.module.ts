import { Module } from '@nestjs/common';
import { DailyActivityRecordsController } from './daily-activity-records.controller';
import { DailyActivityRecordsService } from './daily-activity-records.service';
import { DatabaseModule } from '@app/database/database.module';
import { DailyActivityRecordsRepository } from './daily-activity-records.respository';
import { AuthModule } from '@app/auth/auth.module';
import { GrpcDailyActivityRecordsController } from './grpc.controller';

@Module({
  imports: [DatabaseModule, AuthModule],
  controllers: [
    DailyActivityRecordsController,
    GrpcDailyActivityRecordsController,
  ],
  providers: [DailyActivityRecordsService, DailyActivityRecordsRepository],
  exports: [DailyActivityRecordsService],
})
export class DailyActivityRecordsModule {}
