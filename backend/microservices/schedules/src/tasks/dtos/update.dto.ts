import { TaskStatus } from '../enums';

export class TaskUpdateDto {
  where: {
    id: string;
    userId?: string;
  };
  fields?: {
    name?: string;
    description?: string | null;
    priority?: number;
    fixed?: boolean;
    dueTo?: string | null;
    repeat?: string | null;
    status?: (typeof TaskStatus)[keyof typeof TaskStatus];
    scheduleId?: string;
    startTime?: string | null;
    endTime?: string | null;
  };
}
