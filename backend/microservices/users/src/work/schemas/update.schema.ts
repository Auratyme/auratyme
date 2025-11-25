import { z } from 'zod';
import { WorkType } from '../enums';

export const workUpdateSchema = z
  .object({
    startTime: z.iso.time().optional().nullable(),
    endTime: z.iso.time().optional().nullable(),
    commuteTimeMinutes: z.int().positive().optional().nullable(),
    type: z.enum(Object.values(WorkType)).optional(),
  })
  .strict()
  .optional();
