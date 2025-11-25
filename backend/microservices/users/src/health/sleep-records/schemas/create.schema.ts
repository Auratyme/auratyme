import { z } from 'zod';
import { SleepPhase } from '../enums';

export const sleepRecordCreateSchema = z
  .object({
    startTime: z.iso.datetime(),
    endTime: z.iso.datetime(),
    phase: z.enum(Object.values(SleepPhase)),
  })
  .strict();
