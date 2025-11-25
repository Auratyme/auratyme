import { ScheduleResponseDto } from './dtos';
import { Schedule as ClientSchedule } from 'contracts';

export class SchedulesMapper {
  static clientToResponseDto(
    clientSchedule: ClientSchedule,
  ): ScheduleResponseDto {
    return {
      ...clientSchedule,
      description:
        clientSchedule.description?.length === 0
          ? null
          : clientSchedule.description,
    };
  }
}
