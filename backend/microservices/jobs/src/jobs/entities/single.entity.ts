import { JobType } from '../enums';

export class SingleJob {
  id: string;
  name: string;
  executionDate: string;
  type: (typeof JobType)[keyof typeof JobType];
}
