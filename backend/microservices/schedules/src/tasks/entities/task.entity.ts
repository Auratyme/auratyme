import { TaskStatus } from '../enums';

export class Task {
  id: string;
  name: string;
  description: string | null;
  status: (typeof TaskStatus)[keyof typeof TaskStatus];
  dueTo: string | null;
  repeat: string | null;
  priority: number;
  fixed: boolean;
  createdAt: string;
  updatedAt: string;
  userId: string;
  scheduleId: string;
  startTime: string | null;
  endTime: string | null;
}
