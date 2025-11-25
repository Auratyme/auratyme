import { z } from 'zod';
import { WorkType } from '../enums';

export const workCreateSchema = z
  .object({
    startTime: z.iso.time().nullable().optional(),
    endTime: z.iso.time().nullable().optional(),
    commuteTimeMinutes: z.int().positive().nullable().optional(),
    type: z.enum(Object.values(WorkType)),
  })
  .strict();
