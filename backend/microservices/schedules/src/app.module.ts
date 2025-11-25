import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';

import { TasksModule } from './tasks/tasks.module';
import { EventsModule } from './events/events.module';
import { SchedulesModule } from './schedules/schedules.module';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { loadConfig } from './config';
import { DatabaseModule } from './database/database.module';
import { JobsModule } from './jobs/jobs.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      load: [loadConfig],
      isGlobal: true,
    }),
    DatabaseModule,
    EventsModule,
    JobsModule,
    TasksModule,
    SchedulesModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
