import { z } from 'zod';

export const mealsFindSchema = z
  .object({
    limit: z.coerce.number().int().nonnegative().default(100),
    page: z.coerce.number().int().nonnegative().default(0),
  })
  .strict();
