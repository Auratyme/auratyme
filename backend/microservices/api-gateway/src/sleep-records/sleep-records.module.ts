import { Module } from '@nestjs/common';
import { SleepRecordsController } from './sleep-records.controller';
import { SleepRecordsService } from './sleep-records.service';

@Module({
  controllers: [SleepRecordsController],
  providers: [SleepRecordsService],
  exports: [SleepRecordsService],
})
export class SleepRecordsModule {}
