import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';

import { AppController } from './app.controller';
import { DatabaseModule } from './database/database.module';
import { loadConfig } from './config';
import { AppService } from './app.service';
import { TaskModule } from './task/task.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [loadConfig],
    }),
    DatabaseModule,
    TaskModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
