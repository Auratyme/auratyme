import { Module } from '@nestjs/common';
import { AuthGuard } from './auth.guard';
import { JwtModule } from '@nestjs/jwt';

@Module({
  imports: [JwtModule.register({})],
  providers: [AuthGuard],
  exports: [JwtModule],
})
export class AuthModule {}
