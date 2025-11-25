import { z } from 'zod';
import { SchedulesConstraints } from '../enums';

export const scheduleCreateSchema = z
  .object({
    name: z.string().max(SchedulesConstraints.MAX_NAME_LENGTH),
    description: z.preprocess((value) => {
      if (typeof value === 'string') {
        if (value.length === 0) {
          return null;
        }
      }
    }, z.string().max(SchedulesConstraints.MAX_DESCRIPTION_LENGTH).optional().nullable().default(null)),
    userId: z.string(),
  })
  .strict();
