import { JobType } from '../enums';

export class CronJob {
  id: string;
  name: string;
  cron: string;
  type: (typeof JobType)[keyof typeof JobType];
}
