import { z } from 'zod';

export const profileCreateSchema = z
  .object({
    // userId: z.string().max(User.MAX_ID_LENGTH),
    birthDate: z.iso.date().nullable().optional(),
    chronotypeMEQ: z.int().optional().nullable(),
  })
  .strict();
