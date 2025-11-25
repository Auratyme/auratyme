import { Module } from '@nestjs/common';
import { JobsService } from './jobs.service';
import { BullModule } from '@nestjs/bullmq';
import { JobsController } from './jobs.controller';
import { JobsConsumer } from './jobs.consumer';

import { loadConfig } from '@app/config';
import { BrokerModule } from '@app/broker/broker.module';

@Module({
  imports: [
    BrokerModule,
    BullModule.forRoot({
      connection: {
        host: loadConfig().db.host,
        port: loadConfig().db.port,
      },
    }),
    BullModule.registerQueue({
      name: loadConfig().broker.jobsQueueName,
    }),
  ],
  controllers: [JobsController],
  providers: [JobsService, JobsConsumer],
})
export class JobsModule {}
