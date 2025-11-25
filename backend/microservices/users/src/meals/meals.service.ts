import { Injectable } from '@nestjs/common';
import { MealsRepository } from './meals.repository';
import { Meal } from './entities';
import { MealCreateDto, MealUpdateDto } from './dtos';
import { MealsMapper } from './meals.mapper';
import { MealNotFoundException } from './exceptions';
import { MealsFindOptions } from './types/options/find.type';

@Injectable()
export class MealsService {
  constructor(private readonly mealsRepository: MealsRepository) {}

  async find(options: MealsFindOptions): Promise<Meal[]> {
    const meals = await this.mealsRepository.find(options);

    return meals.map((dbMeal) => MealsMapper.dbToDomain(dbMeal));
  }

  async findOne(id: string): Promise<Meal> {
    const dbMeal = await this.mealsRepository.findOne(id);

    if (!dbMeal) {
      throw new MealNotFoundException(id);
    }

    return MealsMapper.dbToDomain(dbMeal);
  }

  async create(createDto: MealCreateDto): Promise<Meal> {
    const savedDbMeal = await this.mealsRepository.create(createDto);

    return MealsMapper.dbToDomain(savedDbMeal);
  }

  async update(updateDto: MealUpdateDto): Promise<Meal> {
    const updatedDbMeal = await this.mealsRepository.update(updateDto);

    if (!updatedDbMeal) {
      throw new MealNotFoundException(updateDto.id);
    }

    return MealsMapper.dbToDomain(updatedDbMeal);
  }

  async remove(id: string): Promise<Meal> {
    const removedDbMeal = await this.mealsRepository.remove(id);

    if (!removedDbMeal) {
      throw new MealNotFoundException(id);
    }

    return MealsMapper.dbToDomain(removedDbMeal);
  }
}
