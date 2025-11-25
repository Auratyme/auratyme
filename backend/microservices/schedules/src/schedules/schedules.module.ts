import { forwardRef, Module } from '@nestjs/common';

import { SchedulesService } from './schedules.service';
import { SchedulesRepository } from './schedules.repository';
import { DatabaseModule } from '../database/database.module';
import { TasksModule } from '../tasks/tasks.module';
import { SchedulesController } from './schedules.controller';

@Module({
  imports: [DatabaseModule, forwardRef(() => TasksModule)],
  controllers: [SchedulesController],
  providers: [SchedulesRepository, SchedulesService],
  exports: [SchedulesService, SchedulesRepository],
})
export class SchedulesModule {}
