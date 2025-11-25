import { forwardRef, Module } from '@nestjs/common';

import { TasksService } from './tasks.service';
import { TasksRepository } from './tasks.repository';
import { TaskEventsController } from './events.controller';
import { DatabaseModule } from '../database/database.module';
import { JobsModule } from '../jobs/jobs.module';
import { EventsModule } from '../events/events.module';
import { SchedulesModule } from '../schedules/schedules.module';
import { TasksController } from './tasks.controller';

@Module({
  imports: [
    DatabaseModule,
    JobsModule,
    EventsModule,
    forwardRef(() => SchedulesModule),
  ],
  controllers: [TaskEventsController, TasksController],
  providers: [TasksService, TasksRepository],
  exports: [TasksService, TasksRepository],
})
export class TasksModule {}
