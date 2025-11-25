import { Module } from '@nestjs/common';
import { PulseRecordsService } from './pulse-records.service';
import { PulseRecordsController } from './pulse-records.controller';
import { PulseRecordsRepository } from './pulse-records.repository';
import { DatabaseModule } from '@app/database/database.module';
import { AuthModule } from '@app/auth/auth.module';
import { GrpcPulseRecordsController } from './grpc.controller';

@Module({
  imports: [DatabaseModule, AuthModule],
  providers: [
    PulseRecordsService,
    PulseRecordsRepository,
    GrpcPulseRecordsController,
  ],
  controllers: [PulseRecordsController],
  exports: [PulseRecordsService],
})
export class PulseRecordsModule {}
