import { UserContraints } from '@app/users/enums';
import { z } from 'zod';

export const userRemoveSchema = z
  .object({
    where: z
      .object({
        id: z.string().max(UserContraints.MAX_ID_LENGTH),
      })
      .strict(),
  })
  .strict();
