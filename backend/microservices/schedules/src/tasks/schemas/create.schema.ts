import { z } from 'zod';
import { TaskStatus as ClientTaskStatus } from 'contracts';
import { cronSchema } from '@/src/common/schemas';

export const taskCreateSchema = z
  .object({
    name: z.string().max(255),
    userId: z.string(),
    scheduleId: z.uuid(),
    description: z.preprocess((value) => {
      if (typeof value === 'string') {
        if (value.length === 0) {
          return null;
        }
      }
    }, z.string().optional().nullable().default(null)),
    dueTo: z.preprocess((value) => {
      if (typeof value === 'string') {
        if (value.length === 0) {
          return null;
        }
      }
    }, z.iso.datetime().optional().nullable().default(null)),
    repeat: z.preprocess((value) => {
      if (typeof value === 'string') {
        if (value.length === 0) {
          return null;
        }
      }
    }, cronSchema.optional().nullable().default(null)),
    startTime: z.preprocess((value) => {
      if (typeof value === 'string') {
        if (value.length === 0) {
          return null;
        }
      }
    }, z.iso.time().optional().nullable().default(null)),
    endTime: z.preprocess((value) => {
      if (typeof value === 'string') {
        if (value.length === 0) {
          return null;
        }
      }
    }, z.iso.time().optional().nullable().default(null)),
    priority: z.int().optional().default(0),
    fixed: z.boolean().optional().default(false),
    status: z
      .enum(ClientTaskStatus)
      .optional()
      .default(ClientTaskStatus.NOT_STARTED),
  })
  .strict();
