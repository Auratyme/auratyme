export class RoutineUpdateDto {
  id: string;
  fields?: {
    name?: string;
    durationMinutes?: number | null;
  };
}
