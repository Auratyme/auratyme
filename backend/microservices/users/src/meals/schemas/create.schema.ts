import { z } from 'zod';

export const mealCreateSchema = z
  .object({
    name: z.string().max(255),
    startTime: z.iso.time().nullable().optional(),
    durationMinutes: z.int().nullable().optional(),
  })
  .strict();
