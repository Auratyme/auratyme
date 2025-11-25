import { z } from 'zod';
import { TaskStatus as ClientTaskStatus } from 'contracts';
import { cronSchema } from '@/src/common/schemas';

export const taskUpdateSchema = z
  .object({
    where: z.object({
      id: z.uuid(),
      userId: z.string().optional(),
    }),
    fields: z
      .object({
        name: z.string().optional(),
        description: z.preprocess((value) => {
          if (typeof value === 'string') {
            if (value.length === 0) {
              return null;
            }
          }
        }, z.string().optional()),
        scheduleId: z.uuid().optional(),
        priority: z.int().optional(),
        fixed: z.boolean().optional(),
        dueTo: z.preprocess((value) => {
          if (typeof value === 'string') {
            if (value.length === 0) {
              return null;
            }
          }
        }, z.iso.datetime().optional()),
        repeat: z.preprocess((value) => {
          if (typeof value === 'string') {
            if (value.length === 0) {
              return null;
            }
          }
        }, cronSchema.optional()),
        status: z
          .enum(ClientTaskStatus)
          .optional()
          .default(ClientTaskStatus.NOT_STARTED),
      })
      .optional(),
    startTime: z.preprocess((value) => {
      if (typeof value === 'string') {
        if (value.length === 0) {
          return null;
        }
      }
    }, z.iso.time().optional().nullable()),
    endTime: z.preprocess((value) => {
      if (typeof value === 'string') {
        if (value.length === 0) {
          return null;
        }
      }
    }, z.iso.time().optional().nullable()),
  })
  .strict();
