import { z } from 'zod';
import { TaskStatus } from '../enums';

export const orderByTasksSchema = z.enum([
  'createdAt',
  'dueTo',
  'updatedAt',
  'name',
  'status',
  'repeat',
]);

export const taskStatusFilterSchema = z
  .array(z.enum(Object.values(TaskStatus)))
  .refine((items) => new Set(items).size === items.length, {
    message: 'Must be array of unique statuses',
  })
  .or(z.enum(Object.values(TaskStatus)));
