import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ConfigService } from '@nestjs/config';
import { AppConfig } from './common/types';
import { VersioningType } from '@nestjs/common';
import { HttpRequestInterceptor } from './common/interceptors';
import { HttpExceptionFilter } from './common/filters';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { UsersConfig } from 'contracts/users/v1/users.js';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const configService = app.get(ConfigService);
  const appConfig = configService.get<AppConfig>('app')!;

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.GRPC,
    options: {
      package: [
        UsersConfig.PACKAGE,
        'sleep_record',
        'daily_activity_record',
        'pulse_record',
      ],
      protoPath: [
        `/usr/src/app${UsersConfig.PROTO_PATH}`,
        '/usr/src/app/libs/proto/users/v1/sleep-records.proto',
        '/usr/src/app/libs/proto/users/v1/daily-activity-records.proto',
        '/usr/src/app/libs/proto/users/v1/pulse-records.proto',
      ],
      url: UsersConfig.URL,
    },
  });

  app.useGlobalInterceptors(new HttpRequestInterceptor());
  app.useGlobalFilters(new HttpExceptionFilter());
  app.enableShutdownHooks();
  app.enableVersioning({ type: VersioningType.URI });

  await app.startAllMicroservices();
  await app.listen(appConfig.port);
}
bootstrap();
