import { SleepRecordResponseDto } from './dtos';
import { SleepRecord } from './entities';
import { DbSleepRecord } from './types';

export class SleepRecordsMapper {
  static dbToDomain(dbSleepRecord: DbSleepRecord): SleepRecord {
    return {
      ...dbSleepRecord,
      startTime: dbSleepRecord.startTime.toISOString(),
      endTime: dbSleepRecord.endTime.toISOString(),
    };
  }

  static domainToResponseDto(sleepRecord: SleepRecord): SleepRecordResponseDto {
    return sleepRecord;
  }
}
