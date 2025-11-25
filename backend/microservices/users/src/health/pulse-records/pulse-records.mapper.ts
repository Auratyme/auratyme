import { PulseRecordResponseDto } from './dtos';
import { PulseRecord } from './entities';
import { DbPulseRecord } from './types/db-pulse-record';

export class PulseRecordsMapper {
  static dbToDomain(dbPulseRecord: DbPulseRecord): PulseRecord {
    return {
      ...dbPulseRecord,
      timestamp: dbPulseRecord.timestamp.toISOString(),
    };
  }

  static domainToResponseDto(pulseRecord: PulseRecord): PulseRecordResponseDto {
    return pulseRecord;
  }
}
