import { Module } from '@nestjs/common';
import { JobsService } from './jobs.service';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { JobsRepository } from './jobs.repository';
import { DatabaseModule } from '../database/database.module';
import { DiToken } from '../common/enums';
import { JobsConfig } from 'contracts';

@Module({
  imports: [
    ClientsModule.register([
      {
        transport: Transport.GRPC,
        name: DiToken.JOB_CLIENT,
        options: {
          package: JobsConfig.PACKAGE,
          protoPath: `/usr/src/app${JobsConfig.PROTO_PATH}`,
          url: JobsConfig.URL,
        },
      },
    ]),
    DatabaseModule,
  ],
  providers: [JobsService, JobsRepository],
  exports: [JobsService],
})
export class JobsModule {}
