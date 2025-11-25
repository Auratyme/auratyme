export class ScheduleRemoveDto {
  where: {
    id: string;
    userId?: string;
  };
  options?: {
    force?: boolean;
  };
}
