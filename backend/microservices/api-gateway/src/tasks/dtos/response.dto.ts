import { TaskStatus } from '../enums';

export class TaskResponseDto {
  id: string;
  name: string;
  description: string | null;
  status: (typeof TaskStatus)[keyof typeof TaskStatus];
  dueTo: string | null;
  repeat: string | null;
  createdAt: string;
  updatedAt: string;
  scheduleId: string;
  startTime: string | null;
  endTime: string | null;
}
