import { Module } from '@nestjs/common';
import { SchedulesController } from './schedules.controller';
import { SchedulesService } from './schedules.service';
import { AuthModule } from '../auth/auth.module';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { Options } from '@grpc/proto-loader';
import { DiToken } from '../common/enums';
import { SchedulesConfig } from 'contracts';

@Module({
  imports: [
    AuthModule,
    ClientsModule.register([
      {
        name: DiToken.SCHEDULE_PACKAGE,
        transport: Transport.GRPC,
        options: {
          package: SchedulesConfig.PACKAGE,
          protoPath: `/usr/src/app${SchedulesConfig.PROTO_PATH}`,
          url: SchedulesConfig.URL,
          loader: { defaults: true } as Options,
        },
      },
    ]),
  ],
  controllers: [SchedulesController],
  providers: [SchedulesService],
})
export class SchedulesModule {}
