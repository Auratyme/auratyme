import { Module } from '@nestjs/common';
import { UsersService } from './users.service';
import { UsersRepository } from './users.repository';
import { DatabaseModule } from '@app/database/database.module';
import { AuthModule } from '@app/auth/auth.module';
import { UsersController } from './users.controller';

@Module({
  imports: [DatabaseModule, AuthModule],
  providers: [UsersService, UsersRepository],
  controllers: [UsersController],
  exports: [UsersService],
})
export class UsersModule {}
