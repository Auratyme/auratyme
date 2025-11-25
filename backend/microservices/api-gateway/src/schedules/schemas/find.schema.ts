import { SchedulesOrderBy } from 'contracts';
import { z } from 'zod';

export const schedulesFindSchema = z
  .object({
    orderBy: z.enum(SchedulesOrderBy).default(SchedulesOrderBy.CREATED_AT),
    sortBy: z.enum(['asc', 'desc']).optional().default('desc'),
    limit: z.coerce.number().min(5).max(100).default(50),
    page: z.coerce.number().nonnegative().default(0),
  })
  .strict();
