import { z } from 'zod';

export const routineCreateSchema = z
  .object({
    name: z.string().max(255),
    durationMinutes: z.int().positive().nullable().optional(),
  })
  .strict();
