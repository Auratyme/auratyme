import { MealResponseDto } from './dtos';
import { Meal } from './entities';
import { DbMeal } from './types/db.type';

export class MealsMapper {
  static dbToDomain(dbMeal: DbMeal): Meal {
    return dbMeal;
  }

  static domainToResponseDto(meal: Meal): MealResponseDto {
    return {
      durationMinutes: meal.durationMinutes,
      id: meal.id,
      startTime: meal.startTime,
      name: meal.name,
    };
  }
}
