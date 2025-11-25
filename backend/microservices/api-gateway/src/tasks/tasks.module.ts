import { Module } from '@nestjs/common';
import { TasksController } from './tasks.controller';
import { TasksService } from './tasks.service';
import { AuthModule } from '../auth/auth.module';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { Options } from '@grpc/proto-loader';
import { DiToken } from '../common/enums';
import { TasksConfig } from 'contracts';

@Module({
  imports: [
    AuthModule,
    ClientsModule.register([
      {
        name: DiToken.TASK_PACKAGE,
        transport: Transport.GRPC,
        options: {
          package: TasksConfig.PACKAGE,
          protoPath: `/usr/src/app${TasksConfig.PROTO_PATH}`,
          url: TasksConfig.URL,
          loader: { defaults: true, json: true } as Options,
        },
      },
    ]),
  ],
  controllers: [TasksController],
  providers: [TasksService],
})
export class TasksModule {}
