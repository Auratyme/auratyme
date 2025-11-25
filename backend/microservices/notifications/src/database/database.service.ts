import { Inject, Injectable } from '@nestjs/common';
import { NodePgDatabase } from 'drizzle-orm/node-postgres';

import * as schema from './schemas';
import { constants } from '@app/common/constants';
import { Pool } from 'pg';

@Injectable()
export class DatabaseService {
  constructor(
    @Inject(constants.DRIZZLE)
    private readonly db: NodePgDatabase<typeof schema>,
    @Inject(constants.PG_POOL)
    private readonly pool: Pool,
  ) {}

  getDb() {
    return this.db;
  }

  async close() {
    await this.pool.end();
  }
}
