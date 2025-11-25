import { UserContraints } from '@app/users/enums';
import { z } from 'zod';

export const userCreateSchema = z
  .object({
    name: z.string().max(UserContraints.MAX_NAME_LENGTH),
    id: z.string().max(UserContraints.MAX_ID_LENGTH),
  })
  .strict();
