import {
  Body,
  Controller,
  Delete,
  Get,
  HttpStatus,
  InternalServerErrorException,
  NotFoundException,
  Param,
  Patch,
  Post,
  Query,
  Res,
  UseGuards,
} from '@nestjs/common';

import { MealsService } from './meals.service';
import { MealResponseDto } from './dtos';
import { MealsMapper } from './meals.mapper';
import { MealNotFoundException } from './exceptions';
import { Request, Response } from 'express';
import { ZodValidationPipe } from '@app/common/pipes';
import { mealCreateSchema, mealsFindSchema, mealUpdateSchema } from './schemas';
import { AuthGuard } from '@app/auth/auth.guard';
import { User } from '@app/common/decorators';
import z from 'zod';

@UseGuards(AuthGuard)
@Controller({ path: 'meals', version: '1' })
export class MealsController {
  constructor(private readonly mealsService: MealsService) {}

  @Get()
  async find(
    @Res({ passthrough: true }) res: Response,
    @User() user: Request['auth']['user'],
    @Query(new ZodValidationPipe(mealsFindSchema))
    query: z.infer<typeof mealsFindSchema>,
  ): Promise<MealResponseDto[]> {
    try {
      const result = await this.mealsService.find({
        limit: query.limit,
        page: query.page,
        where: {
          userId: user.id,
        },
      });

      if (result.length <= 0) {
        res.status(HttpStatus.NO_CONTENT);
        return [];
      }

      return result.map((meal) => MealsMapper.domainToResponseDto(meal));
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: 'Failed to retrieve meals',
        },
        { cause: err },
      );
    }
  }

  @Get(':id')
  async findOne(
    @Param('id') id: string,
    @User() user: Request['auth']['user'],
  ): Promise<MealResponseDto> {
    try {
      const result = await this.mealsService.findOne(id);

      return MealsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof MealNotFoundException) {
        throw new NotFoundException({
          message: 'Meal not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to retrieve meal`,
        },
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(mealCreateSchema))
    body: z.infer<typeof mealCreateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<MealResponseDto> {
    try {
      const result = await this.mealsService.create({
        userId: user.id,
        ...body,
      });

      return MealsMapper.domainToResponseDto(result);
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: `Failed to create meal`,
        },
        { cause: err },
      );
    }
  }

  @Patch(':id')
  async update(
    @Param('id') id: string,
    @Body(new ZodValidationPipe(mealUpdateSchema))
    body: z.infer<typeof mealUpdateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<MealResponseDto> {
    try {
      const result = await this.mealsService.update({
        id: id,
        fields: body,
      });

      return MealsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof MealNotFoundException) {
        throw new NotFoundException({
          message: 'Meal not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to update meal`,
        },
        { cause: err },
      );
    }
  }

  @Delete(':id')
  async remove(
    @Param('id') id: string,
    @User() user: Request['auth']['user'],
  ): Promise<MealResponseDto> {
    try {
      const result = await this.mealsService.remove(id);

      return MealsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof MealNotFoundException) {
        throw new NotFoundException({
          message: 'Meal not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to remove meal`,
        },
        { cause: err },
      );
    }
  }
}
