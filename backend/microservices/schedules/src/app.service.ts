import {
  Injectable,
  OnApplicationShutdown,
  OnApplicationBootstrap,
  Logger,
} from '@nestjs/common';

import { DatabaseService } from './database/database.service';

@Injectable()
export class AppService
  implements OnApplicationShutdown, OnApplicationBootstrap
{
  private readonly logger = new Logger(AppService.name);

  constructor(private readonly database: DatabaseService) {}

  async onApplicationBootstrap() {}

  async onApplicationShutdown(): Promise<void> {
    await this.database.close();
    this.logger.log('Closed connection with postgres');
  }
}
