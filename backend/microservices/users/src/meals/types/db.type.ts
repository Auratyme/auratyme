import { mealsTable } from '@app/database/schemas';

export type DbMeal = typeof mealsTable.$inferSelect;
