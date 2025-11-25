import { z } from 'zod';
import { PulseRecord } from '../enums';

export const pulseRecordCreateSchema = z.object({
  pulse: z.int().min(PulseRecord.MIN_PULSE),
  timestamp: z.iso.datetime(),
});
