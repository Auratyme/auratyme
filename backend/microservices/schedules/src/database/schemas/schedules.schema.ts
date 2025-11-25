import { pgTable, varchar } from 'drizzle-orm/pg-core';

import { createdAt, updatedAt, id } from './helpers';
import { SchedulesConstraints } from '@app/schedules/enums';

export const schedulesTable = pgTable('schedules', {
  id,
  name: varchar({ length: SchedulesConstraints.MAX_NAME_LENGTH }).notNull(),
  description: varchar({ length: SchedulesConstraints.MAX_DESCRIPTION_LENGTH }),
  userId: varchar({
    length: SchedulesConstraints.MAX_USER_ID_LENGTH,
  }).notNull(),
  createdAt,
  updatedAt,
});
