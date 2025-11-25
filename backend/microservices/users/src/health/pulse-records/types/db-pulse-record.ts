import { pulseRecordsTable } from '@app/database/schemas/pulse-records.schema';

export type DbPulseRecord = typeof pulseRecordsTable.$inferSelect;
