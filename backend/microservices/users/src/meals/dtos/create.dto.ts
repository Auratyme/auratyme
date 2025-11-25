export class MealCreateDto {
  userId: string;
  name: string;
  startTime?: string | null;
  durationMinutes?: number | null;
}
