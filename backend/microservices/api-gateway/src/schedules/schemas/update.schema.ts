import { z } from 'zod';

export const scheduleUpdateSchema = z
  .object({
    name: z.string().max(255).optional(),
    description: z.string().max(500).optional().nullable(),
  })
  .strict()
  .optional();
