import { UserContraints } from '@app/users/enums';
import { z } from 'zod';

export const userUpdateSchema = z
  .object({
    where: z
      .object({
        id: z.string().max(UserContraints.MAX_ID_LENGTH),
      })
      .strict(),
    fields: z
      .object({
        name: z.string().max(UserContraints.MAX_NAME_LENGTH).optional(),
      })
      .strict()
      .optional(),
  })
  .strict();
