import { Injectable, Logger, OnApplicationShutdown } from '@nestjs/common';

import { DatabaseService } from './database/database.service';

@Injectable()
export class AppService implements OnApplicationShutdown {
  private readonly logger = new Logger(AppService.name);

  constructor(private readonly database: DatabaseService) {}

  async onApplicationShutdown(): Promise<void> {
    try {
      await this.database.close();
      this.logger.log('Database connection closed successfully');
    } catch (err) {
      this.logger.error('Error while closing database connection', err);
    }
  }
}
