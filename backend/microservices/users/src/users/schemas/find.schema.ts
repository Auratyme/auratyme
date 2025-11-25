import { SortType, UsersOrderBy } from 'contracts';
import { z } from 'zod';

export const usersFindSchema = z
  .object({
    options: z
      .object({
        limit: z.coerce.number().int().nonnegative().default(100),
        page: z.coerce.number().int().nonnegative().default(0),
        orderBy: z.enum(UsersOrderBy).default(UsersOrderBy.CREATED_AT),
        sortBy: z.enum(SortType).default(SortType.DESC),
      })
      .strict()
      .optional(),
  })
  .strict();
