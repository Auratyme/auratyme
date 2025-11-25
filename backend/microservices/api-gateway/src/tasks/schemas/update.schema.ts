import { z } from 'zod';

import { TaskStatus } from '../enums';

export const taskUpdateSchema = z
  .object({
    name: z.string().max(255).optional(),
    description: z.string().max(500).optional().nullable(),
    status: z.enum(Object.values(TaskStatus)).optional(),
    dueTo: z.iso.datetime().optional().nullable(),
    repeat: z.string().optional().nullable(),
    scheduleId: z.uuid(),
    priority: z.int().optional(),
    fixed: z.boolean().optional(),
    startTime: z.iso.time().optional().nullable(),
    endTime: z.iso.time().optional().nullable(),
  })
  .strict()
  .optional();
