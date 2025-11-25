import { z } from 'zod';

export const scheduleRemoveSchema = z
  .object({
    force: z.boolean().default(false),
  })
  .strict()
  .optional();
