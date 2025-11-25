import { NestFactory } from '@nestjs/core';
import { VersioningType } from '@nestjs/common';

import { AppModule } from './app.module';
import { HttpExceptionFilter } from './common/filters';
import { ConfigService } from '@nestjs/config';
import { AppConfig, BrokerConfig } from './common/types';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { HttpRequestInterceptor } from './common/interceptors';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const configService = app.get(ConfigService);
  const brokerConfig = configService.get<BrokerConfig>(
    'broker',
  ) as BrokerConfig;
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

  app.enableShutdownHooks();
  app.useGlobalInterceptors(new HttpRequestInterceptor());
  app.useGlobalFilters(new HttpExceptionFilter());
  app.enableVersioning({
    type: VersioningType.URI,
  });

  await app.startAllMicroservices();
  await app.listen(appConfig.port);
}

bootstrap();
