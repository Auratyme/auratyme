import { FindOptions } from 'common';
import { DbMeal } from '../db.type';

export type MealsFindOptions = FindOptions<Partial<DbMeal>, keyof DbMeal>;
