import { AuthModule } from '@app/auth/auth.module';
import { DatabaseModule } from '@app/database/database.module';
import { Module } from '@nestjs/common';
import { MealsController } from './meals.controller';
import { MealsService } from './meals.service';
import { MealsRepository } from './meals.repository';

@Module({
  imports: [DatabaseModule, AuthModule],
  controllers: [MealsController],
  providers: [MealsService, MealsRepository],
  exports: [MealsService],
})
export class MealsModule {}
