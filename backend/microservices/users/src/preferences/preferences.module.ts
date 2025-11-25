import { AuthModule } from '@app/auth/auth.module';
import { DatabaseModule } from '@app/database/database.module';
import { Module } from '@nestjs/common';
import { PreferencesController } from './preferences.controller';
import { PreferencesService } from './preferences.service';
import { PreferencesRepository } from './preferences.repository';

@Module({
  imports: [DatabaseModule, AuthModule],
  controllers: [PreferencesController],
  providers: [PreferencesService, PreferencesRepository],
  exports: [PreferencesService],
})
export class PreferencesModule {}
