import { routinesTable } from '@app/database/schemas';

export type DbRoutine = typeof routinesTable.$inferSelect;
