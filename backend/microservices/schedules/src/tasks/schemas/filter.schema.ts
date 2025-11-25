import { z } from 'zod';

import { datetimeFilterSchema, cronSchema } from '@app/common/schemas';
import { orderByTasksSchema, taskStatusFilterSchema } from './helpers';
import { TaskConstraint } from '../enums';

export const filterTasksSchema = z
  .object({
    orderBy: orderByTasksSchema.optional().default('createdAt'),
    sortBy: z.enum(['asc', 'desc']).optional().default('desc'),
    limit: z
      .number()
      .int()
      .nonnegative()
      .optional()
      .default(TaskConstraint.PAGINATION_LIMIT),
    page: z
      .number()
      .int()
      .nonnegative()
      .optional()
      .default(TaskConstraint.DEFAULT_PAGE),
    where: z
      .object({
        name: z.string().max(TaskConstraint.MAX_NAME_LENGTH).optional(),
        status: taskStatusFilterSchema.optional(),
        repeat: cronSchema.optional(),
        dueTo: datetimeFilterSchema.optional(),
        createdAt: datetimeFilterSchema.optional(),
        updatedAt: datetimeFilterSchema.optional(),
        scheduleId: z.string().uuid().optional(),
      })
      .strict()
      .optional(),
  })
  .strict();
