import { z } from 'zod';

import { SchedulesConstraints } from '../enums';
import { SchedulesOrderBy, SortType } from 'contracts';

export const schedulesFindSchema = z
  .object({
    options: z
      .object({
        orderBy: z
          .enum(SchedulesOrderBy)
          .optional()
          .default(SchedulesOrderBy.CREATED_AT),
        sortBy: z.enum(SortType).optional().default(SortType.DESC),
        limit: z.coerce
          .number()
          .min(SchedulesConstraints.MIN_LIMIT)
          .max(SchedulesConstraints.MAX_LIMIT)
          .default(SchedulesConstraints.DEFAULT_LIMIT),
        page: z.coerce
          .number()
          .nonnegative()
          .default(SchedulesConstraints.DEFAULT_PAGE),
      })
      .optional(),
    where: z
      .object({
        userId: z.string().optional(),
      })
      .optional(),
  })
  .strict();
