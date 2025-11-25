import { loadConfig } from '@app/config';

export type DatabaseConfig = ReturnType<typeof loadConfig>['db'];
