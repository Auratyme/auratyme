import { Module } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

import { DatabaseService } from './database.service';
import { DatabaseConfig } from '@app/common/types';
import * as schema from './schemas';
import { DiToken } from '../common/enums';

@Module({
  providers: [
    {
      provide: DiToken.PG_POOL,
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
      provide: DiToken.DRIZZLE,
      useFactory: (pool: Pool) => {
        return drizzle(pool, { schema });
      },
      inject: [DiToken.PG_POOL],
    },
    DatabaseService,
  ],
  exports: [DiToken.DRIZZLE, DatabaseService],
})
export class DatabaseModule {}
