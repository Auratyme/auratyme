import { AuthModule } from '@app/auth/auth.module';
import { DatabaseModule } from '@app/database/database.module';
import { Module } from '@nestjs/common';
import { WorkController } from './work.controller';
import { WorkService } from './work.service';
import { WorkRepository } from './work.repository';

@Module({
  imports: [DatabaseModule, AuthModule],
  controllers: [WorkController],
  providers: [WorkService, WorkRepository],
  exports: [WorkService],
})
export class WorkModule {}
