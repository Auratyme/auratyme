import { z } from 'zod';

import { SchedulesConstraints } from '../enums';

export const scheduleUpdateSchema = z
  .object({
    where: z.object({
      id: z.uuid(),
      userId: z.string().optional(),
    }),
    fields: z
      .object({
        name: z.string().max(SchedulesConstraints.MAX_NAME_LENGTH).optional(),
        description: z.preprocess((value) => {
          if (typeof value === 'string') {
            if (value.length === 0) {
              return null;
            }
          }
        }, z.string().max(SchedulesConstraints.MAX_DESCRIPTION_LENGTH).optional()),
      })
      .optional(),
  })
  .strict();
