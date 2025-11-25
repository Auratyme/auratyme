import { DailyActivityRecordsModule } from '@app/health/daily-activity-records/daily-activity-records.module';
import { PulseRecordsModule } from '@app/health/pulse-records/pulse-records.module';
import { SleepRecordsModule } from '@app/health/sleep-records/sleep-records.module';
import { Module } from '@nestjs/common';

@Module({
  imports: [DailyActivityRecordsModule, PulseRecordsModule, SleepRecordsModule],
  exports: [DailyActivityRecordsModule, PulseRecordsModule, SleepRecordsModule],
})
export class HealthModule {}
