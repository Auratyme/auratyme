import { TasksOrderBy } from 'contracts';
import { z } from 'zod';

export const tasksFindSchema = z
  .object({
    orderBy: z.enum(TasksOrderBy).default(TasksOrderBy.CREATED_AT),
    sortBy: z.enum(['asc', 'desc']).optional().default('desc'),
    limit: z.coerce.number().min(5).max(100).default(50),
    page: z.coerce.number().nonnegative().default(0),
  })
  .strict();
