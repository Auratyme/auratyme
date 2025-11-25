import { Module } from '@nestjs/common';
import { DailyActivityRecordsController } from './daily-activity-records.controller';
import { DailyActivityRecordsService } from './daily-activity-records.service';

@Module({
  controllers: [DailyActivityRecordsController],
  providers: [DailyActivityRecordsService],
  exports: [DailyActivityRecordsService],
})
export class DailyActivityRecordsModule {}
