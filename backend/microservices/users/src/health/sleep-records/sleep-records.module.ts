import { Module } from '@nestjs/common';
import { SleepRecordsController } from './sleep-records.controller';
import { SleepRecordsService } from './sleep-records.service';
import { SleepRecordsRepository } from './sleep-records.repository';
import { DatabaseModule } from '@app/database/database.module';
import { AuthModule } from '@app/auth/auth.module';
import { GrpcSleepRecordsController } from './grpc.controller';

@Module({
  imports: [DatabaseModule, AuthModule],
  controllers: [SleepRecordsController, GrpcSleepRecordsController],
  providers: [SleepRecordsService, SleepRecordsRepository],
  exports: [SleepRecordsService],
})
export class SleepRecordsModule {}
