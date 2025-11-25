import { AuthModule } from '@app/auth/auth.module';
import { DatabaseModule } from '@app/database/database.module';
import { Module } from '@nestjs/common';
import { ProfilesController } from './profiles.controller';
import { ProfilesService } from './profiles.service';
import { ProfilesRepository } from './profiles.repository';

@Module({
  imports: [DatabaseModule, AuthModule],
  controllers: [ProfilesController],
  providers: [ProfilesService, ProfilesRepository],
  exports: [ProfilesService],
})
export class ProfilesModule {}
