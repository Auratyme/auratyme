import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UsersModule } from './users/users.module';
import { SchedulesModule } from './schedules/schedules.module';
import { TasksModule } from './tasks/tasks.module';
import { PulseRecordsModule } from './pulse-records/pulse-records.module';
import { DailyActivityRecordsModule } from './daily-activity-records/daily-activity-records.module';
import { SleepRecordsModule } from './sleep-records/sleep-records.module';
import { RoutinesModule } from './routines/routines.module';
import { ProfilesModule } from './profiles/profiles.module';
import { MealsModule } from './meals/meals.module';
import { WorkModule } from './work/work.module';
import { PreferencesModule } from './preferences/preferences.module';
import { PushTokensModule } from './push-tokens/push-tokens.module';
import { AuthModule } from './auth/auth.module';
import { ConfigModule } from '@nestjs/config';
import { loadConfig } from './config';

@Module({
  imports: [
    ConfigModule.forRoot({
      load: [loadConfig],
      isGlobal: true,
    }),
    UsersModule,
    SchedulesModule,
    TasksModule,
    PulseRecordsModule,
    DailyActivityRecordsModule,
    SleepRecordsModule,
    RoutinesModule,
    ProfilesModule,
    MealsModule,
    WorkModule,
    PreferencesModule,
    PushTokensModule,
    AuthModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
