import { NestFactory } from '@nestjs/core';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';

import { loadConfig } from './config';
import { AppModule } from './app.module';
import { JobsConfig } from 'contracts';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.GRPC,
    options: {
      package: JobsConfig.PACKAGE,
      protoPath: `/usr/src/app${JobsConfig.PROTO_PATH}`,
      url: JobsConfig.URL,
    },
  });
  app.enableShutdownHooks();

  await app.startAllMicroservices();
  await app.listen(loadConfig().app.port);
}

bootstrap();
