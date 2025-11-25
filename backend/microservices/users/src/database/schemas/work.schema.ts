import { varchar, pgTable, time, pgEnum, integer } from 'drizzle-orm/pg-core';
import { UserContraints } from '@app/users/enums';
import { usersTable } from './users.schema';
import { WorkType } from '@app/work/enums';

export const workTypeEnum = pgEnum('work_type', [
  WorkType.HYBRID,
  WorkType.OFFICE,
  WorkType.REMOTE,
]);

export const workTable = pgTable('work', {
  userId: varchar({ length: UserContraints.MAX_ID_LENGTH })
    .references(() => usersTable.id)
    .notNull()
    .primaryKey(),
  startTime: time({ precision: 0 }),
  endTime: time({ precision: 0 }),
  commuteTimeMinutes: integer(),
  type: workTypeEnum().notNull(),
});
