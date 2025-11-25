import { SortType, TasksOrderBy } from 'contracts';
import { z } from 'zod';

export const tasksFindSchema = z
  .object({
    where: z
      .object({
        userId: z.string().optional(),
      })
      .optional(),
    options: z
      .object({
        limit: z.int().optional().default(50),
        page: z.int().optional().default(0),
        orderBy: z
          .enum(TasksOrderBy)
          .optional()
          .default(TasksOrderBy.CREATED_AT),
        sortBy: z.enum(SortType).optional().default(SortType.DESC),
      })
      .optional(),
  })
  .strict()
  .optional();
