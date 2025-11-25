import { NestFactory } from '@nestjs/core';
import { VersioningType } from '@nestjs/common';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { Options } from '@grpc/proto-loader';

import { AppModule } from './app.module';
import { ConfigService } from '@nestjs/config';
import { AppConfig, Config } from './common/types';

import { SchedulesConfig, TasksConfig } from 'contracts';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const configService = app.get(ConfigService);
  const brokerConfig = configService.get<Config['broker']>(
    'broker',
  ) as Config['broker'];
  const appConfig = configService.get<AppConfig>('app') as AppConfig;

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.RMQ,
    options: {
      urls: [brokerConfig.amqpConnectionString],
      queue: brokerConfig.queueName,
      queueOptions: {
        durable: true,
        autoDelete: false,
        exclusive: false,
      },
      exchange: brokerConfig.exchangeName,
      exchangeType: 'topic',
      wildcards: true,
    },
  });

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.GRPC,
    options: {
      package: [SchedulesConfig.PACKAGE, TasksConfig.PACKAGE],
      protoPath: [
        `/usr/src/app${SchedulesConfig.PROTO_PATH}`,
        `/usr/src/app${TasksConfig.PROTO_PATH}`,
      ],
      url: SchedulesConfig.URL,
      loader: {
        defaults: true,
        arrays: true,
      } as Options,
    },
  });

  app.enableShutdownHooks();
  app.enableVersioning({
    type: VersioningType.URI,
  });

  await app.startAllMicroservices();
  await app.listen(appConfig.port);
}

bootstrap();
