import { RoutineResponseDto } from './dtos';
import { Routine } from './entities';
import { DbRoutine } from './types/db.type';

export class RoutinesMapper {
  static dbToDomain(dbRoutine: DbRoutine): Routine {
    return dbRoutine;
  }

  static domainToResponseDto(routine: Routine): RoutineResponseDto {
    return {
      durationMinutes: routine.durationMinutes,
      id: routine.id,
      name: routine.name,
    };
  }
}
