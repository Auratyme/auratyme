import { z } from 'zod';

export const routinesFindSchema = z
  .object({
    limit: z.coerce.number().int().nonnegative().default(100),
    page: z.coerce.number().int().nonnegative().default(0),
  })
  .strict();
