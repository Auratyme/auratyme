import { z } from 'zod';

export const scheduleCreateSchema = z
  .object({
    name: z.string().max(255),
    description: z.string().max(500).nullable().default(null),
  })
  .strict();
