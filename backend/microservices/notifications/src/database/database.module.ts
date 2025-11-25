import { Module } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

import { DatabaseService } from './database.service';
import { constants } from '@app/common/constants';
import { DatabaseConfig } from '@app/common/types';
import * as schema from './schemas';

@Module({
  providers: [
    {
      provide: constants.PG_POOL,
      useFactory: (configService: ConfigService) => {
        const dbConfig = configService.get<DatabaseConfig>('db')!;

        const pool = new Pool({
          host: dbConfig.host,
          user: dbConfig.user,
          password: dbConfig.password,
          port: dbConfig.port,
          database: dbConfig.name,
        });

        return pool;
      },
      inject: [ConfigService],
    },
    {
      provide: constants.DRIZZLE,
      useFactory: (pool: Pool) => {
        return drizzle(pool, { schema });
      },
      inject: [constants.PG_POOL],
    },
    DatabaseService,
  ],
  exports: [constants.DRIZZLE, DatabaseService],
})
export class DatabaseModule {}
