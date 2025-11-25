import { loadConfig } from '@app/config';

export type AuthConfig = ReturnType<typeof loadConfig>['auth'];
