import { DailyActivityRecordResponseDto } from './dtos';
import { DailyActivityRecord } from './entities';
import { DbDailyActivityRecord } from './types';

export class DailyActivityRecordsMapper {
  static dbToDomain(
    dbDailyActivityRecord: DbDailyActivityRecord,
  ): DailyActivityRecord {
    return {
      ...dbDailyActivityRecord,
      date: dbDailyActivityRecord.date.toISOString(),
    };
  }

  static domainToResponseDto(
    dailyActivityRecord: DailyActivityRecord,
  ): DailyActivityRecordResponseDto {
    return dailyActivityRecord;
  }
}
