import { loadConfig } from '@app/config';

export type AppConfig = ReturnType<typeof loadConfig>['app'];
