import { WorkResponseDto } from './dtos';
import { Work } from './entities';
import { DbWork } from './types/db.type';

export class WorkMapper {
  static dbToDomain(dbWork: DbWork): Work {
    return dbWork;
  }

  static domainToResponseDto(work: Work): WorkResponseDto {
    return {
      type: work.type,
      commuteTimeMinutes: work.commuteTimeMinutes,
      endTime: work.endTime,
      startTime: work.startTime,
    };
  }
}
