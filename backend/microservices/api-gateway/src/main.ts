import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { VersioningType } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { AppConfig } from './common/types';
import { HttpExceptionFilter, HttpRequestInterceptor } from 'common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);

  const appConfig = configService.get('app') as AppConfig;

  app.useGlobalInterceptors(new HttpRequestInterceptor());
  app.useGlobalFilters(new HttpExceptionFilter());
  app.enableShutdownHooks();
  app.enableVersioning({ type: VersioningType.URI });

  await app.listen(appConfig.port);
}
bootstrap();
