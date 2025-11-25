import { MealException } from './meal.exception';

export class MealNotFoundException extends MealException {
  constructor(id: string) {
    super(`meal with id = ${id} was not found`);
  }
}
