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

import { RoutinesService } from './routines.service';
import { RoutineCreateDto, RoutineResponseDto } from './dtos';
import { RoutinesMapper } from './routines.mapper';
import { RoutineNotFoundException } from './exceptions';
import { Request, Response } from 'express';
import { ZodValidationPipe } from '@app/common/pipes';
import {
  routineCreateSchema,
  routinesFindSchema,
  routineUpdateSchema,
} from './schemas';
import { AuthGuard } from '@app/auth/auth.guard';
import { User } from '@app/common/decorators';
import z from 'zod';

@UseGuards(AuthGuard)
@Controller({ path: 'routines', version: '1' })
export class RoutinesController {
  constructor(private readonly routinesService: RoutinesService) {}

  @Get()
  async find(
    @Res({ passthrough: true }) res: Response,
    @User() user: Request['auth']['user'],
    @Query(new ZodValidationPipe(routinesFindSchema))
    query: z.infer<typeof routinesFindSchema>,
  ): Promise<RoutineResponseDto[]> {
    try {
      const result = await this.routinesService.find({
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

      return result.map((routine) =>
        RoutinesMapper.domainToResponseDto(routine),
      );
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: 'Failed to retrieve routines',
        },
        { cause: err },
      );
    }
  }

  @Get(':id')
  async findOne(
    @Param('id') id: string,
    @User() user: Request['auth']['user'],
  ): Promise<RoutineResponseDto> {
    try {
      const result = await this.routinesService.findOne(id);

      return RoutinesMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof RoutineNotFoundException) {
        throw new NotFoundException({
          message: 'Routine not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to retrieve routine`,
        },
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(routineCreateSchema)) body: RoutineCreateDto,
    @User() user: Request['auth']['user'],
  ): Promise<RoutineResponseDto> {
    try {
      const result = await this.routinesService.create({
        userId: user.id,
        name: body.name,
        durationMinutes: body.durationMinutes,
      });

      return RoutinesMapper.domainToResponseDto(result);
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: `Failed to create routine`,
        },
        { cause: err },
      );
    }
  }

  @Patch(':id')
  async update(
    @Param('id') id: string,
    @Body(new ZodValidationPipe(routineUpdateSchema))
    body: z.infer<typeof routineUpdateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<RoutineResponseDto> {
    try {
      const result = await this.routinesService.update({
        id: id,
        fields: body,
      });

      return RoutinesMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof RoutineNotFoundException) {
        throw new NotFoundException({
          message: 'Routine not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to update routine`,
        },
        { cause: err },
      );
    }
  }

  @Delete(':id')
  async remove(
    @Param('id') id: string,
    @User() user: Request['auth']['user'],
  ): Promise<RoutineResponseDto> {
    try {
      const result = await this.routinesService.remove(id);

      return RoutinesMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof RoutineNotFoundException) {
        throw new NotFoundException({
          message: 'Routine not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to remove routine`,
        },
        { cause: err },
      );
    }
  }
}
