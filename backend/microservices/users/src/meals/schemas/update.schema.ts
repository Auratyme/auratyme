import { z } from 'zod';

export const mealUpdateSchema = z
  .object({
    name: z.string().max(255).optional(),
    startTime: z.iso.time().nullable().optional(),
    durationMinutes: z.int().nullable().optional(),
  })
  .strict()
  .optional();
