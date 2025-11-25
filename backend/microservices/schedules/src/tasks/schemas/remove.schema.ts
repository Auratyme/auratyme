import { z } from 'zod';

export const taskRemoveSchema = z
  .object({
    where: z.object({
      id: z.uuid(),
      userId: z.string().optional(),
    }),
  })
  .strict();
