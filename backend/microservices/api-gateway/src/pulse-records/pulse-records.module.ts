import { Module } from '@nestjs/common';
import { PulseRecordsController } from './pulse-records.controller';
import { PulseRecordsService } from './pulse-records.service';

@Module({
  controllers: [PulseRecordsController],
  providers: [PulseRecordsService],
  exports: [PulseRecordsService],
})
export class PulseRecordsModule {}
