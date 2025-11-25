import { Inject, Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { NodePgDatabase } from 'drizzle-orm/node-postgres';

import * as schema from './schemas';
import { DiToken } from '../common/enums';
import { Pool } from 'pg';
import { DatabaseConfig } from '../common/types';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class DatabaseService implements OnModuleInit {
  private readonly dbConfig: DatabaseConfig;
  private readonly logger = new Logger(DatabaseService.name);

  constructor(
    @Inject(DiToken.DRIZZLE)
    private readonly db: NodePgDatabase<typeof schema>,
    @Inject(DiToken.PG_POOL)
    private readonly pool: Pool,
    private readonly configService: ConfigService,
  ) {
    this.dbConfig = this.configService.get<DatabaseConfig>(
      'db',
    ) as DatabaseConfig;
  }

  onModuleInit() {
    this.logger.log(
      `Connected to postgres on url: postgres://${this.dbConfig.user}:***@${this.dbConfig.host}:${this.dbConfig.port}/${this.dbConfig.name}`,
    );
  }

  getDb() {
    return this.db;
  }

  async close() {
    await this.pool.end();
  }
}
