import { z } from 'zod';

export const routineUpdateSchema = z
  .object({
    name: z.string().max(255).optional(),
    durationMinutes: z.int().positive().nullable().optional(),
  })
  .strict()
  .optional();
