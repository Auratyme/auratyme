import { timestamp, uuid } from 'drizzle-orm/pg-core';

export const createdAt = timestamp().notNull().defaultNow();
export const updatedAt = timestamp()
  .notNull()
  .defaultNow()
  .$onUpdateFn(() => new Date());
export const id = uuid().defaultRandom().primaryKey();
