import { AppConfig } from './app-config.type';
import { AuthConfig } from './auth-config.type';
import { BrokerConfig } from './broker-config.type';
import { DatabaseConfig } from './db-config.type';

export type Config = {
  app: AppConfig;
  db: DatabaseConfig;
  auth: AuthConfig;
  broker: BrokerConfig;
  jobsClient: {
    connectionString: string;
  };
};
