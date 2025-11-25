import { Injectable } from '@nestjs/common';
import { MealCreateDto, MealUpdateDto } from './dtos';
import { Database } from '@app/database/types';
import { DatabaseService } from '@app/database/database.service';
import { DbMeal } from './types/db.type';
import { mealsTable } from '@app/database/schemas';
import { eq, asc, desc } from 'drizzle-orm';
import { MealsFindOptions } from './types/options/find.type';

@Injectable()
export class MealsRepository {
  private readonly db: Database;

  constructor(readonly databaseService: DatabaseService) {
    this.db = databaseService.getDb();
  }

  async find(options: MealsFindOptions): Promise<DbMeal[]> {
    const limit = options.limit || 100;
    const page = options.page || 0;
    const sortBy = options.sortBy || 'desc';
    const orderBy = options.orderBy || 'startTime';
    const userId = options.where?.userId;

    const result = await this.db
      .select()
      .from(mealsTable)
      .limit(limit)
      .offset(limit * page)
      .where(userId ? eq(mealsTable.userId, userId) : undefined)
      .orderBy(
        sortBy === 'asc' ? asc(mealsTable[orderBy]) : desc(mealsTable[orderBy]),
      );

    return result;
  }

  async findOne(id: string): Promise<DbMeal | null> {
    const result = await this.db
      .select()
      .from(mealsTable)
      .where(eq(mealsTable.id, id));

    return result.length <= 0 ? null : result[0];
  }

  async create(createDto: MealCreateDto): Promise<DbMeal> {
    const result = await this.db
      .insert(mealsTable)
      .values(createDto)
      .returning();

    return result[0];
  }

  async update(updateDto: MealUpdateDto): Promise<DbMeal | null> {
    const fields = updateDto.fields || {};

    const result = await this.db
      .update(mealsTable)
      .set({
        durationMinutes: fields.durationMinutes,
        name: fields.name,
        startTime: fields.startTime,
      })
      .where(eq(mealsTable.id, updateDto.id))
      .returning();

    return result.length <= 0 ? null : result[0];
  }

  async remove(id: string): Promise<DbMeal | null> {
    const result = await this.db
      .delete(mealsTable)
      .where(eq(mealsTable.id, id))
      .returning();

    return result.length <= 0 ? null : result[0];
  }
}
