import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';

import { AppController } from './app.controller';
import { AppService } from './app.service';
import { loadConfig } from './config';
import { JobsModule } from './jobs/jobs.module';
import { BrokerModule } from './broker/broker.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      load: [loadConfig],
      isGlobal: true,
    }),
    JobsModule,
    BrokerModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
