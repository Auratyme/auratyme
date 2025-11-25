import { z } from 'zod';

export const scheduleRemoveSchema = z
  .object({
    where: z.object({
      id: z.uuid(),
      userId: z.string().optional(),
    }),
    options: z
      .object({
        force: z.boolean().default(false),
      })
      .optional(),
  })
  .strict();
