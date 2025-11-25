import { z } from 'zod';

export const taskEventsSchema = z
  .object({
    userId: z.string().optional(),
  })
  .strict()
  .optional();
