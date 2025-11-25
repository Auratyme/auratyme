import { z } from 'zod';
import { TaskStatus } from '../enums';

export const taskCreateSchema = z
  .object({
    name: z.string().max(255),
    description: z.string().max(500).nullable().default(null),
    status: z.enum(Object.values(TaskStatus)).optional().default('not-started'),
    dueTo: z.iso.datetime().optional().nullable().default(null),
    repeat: z.string().optional().nullable().default(null),
    scheduleId: z.uuid(),
    priority: z.int().optional().default(0),
    fixed: z.boolean().optional().default(false),
    startTime: z.iso.time().optional().nullable().default(null),
    endTime: z.iso.time().optional().nullable().default(null),
  })
  .strict();
