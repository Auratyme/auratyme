import { z } from 'zod';

export const scheduleFindOneSchema = z.object({
  where: z.object({
    id: z.uuid(),
    userId: z.string().optional(),
  }),
});
