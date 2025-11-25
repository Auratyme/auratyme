import { UserContraints } from '@app/users/enums';
import { timestamp, varchar } from 'drizzle-orm/pg-core';

export const createdAt = timestamp().defaultNow().notNull();
export const updatedAt = timestamp()
  .notNull()
  .defaultNow()
  .$onUpdateFn(() => new Date());
export const userId = varchar({
  length: UserContraints.MAX_ID_LENGTH,
}).notNull();
