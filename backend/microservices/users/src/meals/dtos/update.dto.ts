export class MealUpdateDto {
  id: string;
  fields?: {
    name?: string;
    startTime?: string | null;
    durationMinutes?: number | null;
  };
}
