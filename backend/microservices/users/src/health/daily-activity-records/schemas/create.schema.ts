import { z } from 'zod';

export const dailyActivityRecordCreateSchema = z
  .object({
    steps: z.int().nonnegative().min(0),
    date: z.iso.datetime(),
  })
  .strict();
