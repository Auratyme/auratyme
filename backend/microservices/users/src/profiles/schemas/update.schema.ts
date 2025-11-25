import { z } from 'zod';

export const profilesUpdateSchema = z
  .object({
    // userId: z.string().max(User.MAX_ID_LENGTH),
    birthDate: z.iso.date().nullable().optional(),
    chronotypeMEQ: z.int().optional().nullable(),
  })
  .strict()
  .optional();
