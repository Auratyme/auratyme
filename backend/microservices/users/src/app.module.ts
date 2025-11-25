import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { DatabaseModule } from './database/database.module';
import { ConfigModule } from '@nestjs/config';
import { loadConfig } from './config';
import { UsersModule } from './users/users.module';
import { HealthModule } from './health/health.module';
import { ProfilesModule } from './profiles/profiles.module';
import { PreferencesModule } from './preferences/preferences.module';
import { RoutinesModule } from './routines/routines.module';
import { MealsModule } from './meals/meals.module';
import { WorkModule } from './work/work.module';

@Module({
  imports: [
    DatabaseModule,
    ConfigModule.forRoot({
      load: [loadConfig],
      isGlobal: true,
    }),
    UsersModule,
    HealthModule,
    ProfilesModule,
    PreferencesModule,
    MealsModule,
    WorkModule,
    RoutinesModule,
  ],
  controllers: [AppController],
})
export class AppModule {}
