import {
  Body,
  Controller,
  Delete,
  Get,
  InternalServerErrorException,
  NotFoundException,
  Patch,
  Post,
  UseGuards,
} from '@nestjs/common';

import { WorkService } from './work.service';
import { WorkResponseDto } from './dtos';
import { WorkMapper } from './work.mapper';
import { WorkNotFoundException } from './exceptions';
import { Request } from 'express';
import { ZodValidationPipe } from '@app/common/pipes';
import { workCreateSchema, workUpdateSchema } from './schemas';
import { AuthGuard } from '@app/auth/auth.guard';
import { User } from '@app/common/decorators';
import z from 'zod';

@UseGuards(AuthGuard)
@Controller({ path: 'work', version: '1' })
export class WorkController {
  constructor(private readonly workService: WorkService) {}

  @Get()
  async findForUser(
    @User() user: Request['auth']['user'],
  ): Promise<WorkResponseDto> {
    try {
      const result = await this.workService.findForUser(user.id);

      return WorkMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof WorkNotFoundException) {
        throw new NotFoundException({
          message: 'Work not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: 'Failed to retrieve work',
        },
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(workCreateSchema))
    body: z.infer<typeof workCreateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<WorkResponseDto> {
    try {
      const result = await this.workService.create({
        userId: user.id,
        ...body,
      });

      return WorkMapper.domainToResponseDto(result);
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: `Failed to create work`,
        },
        { cause: err },
      );
    }
  }

  @Patch()
  async update(
    @Body(new ZodValidationPipe(workUpdateSchema))
    body: z.infer<typeof workUpdateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<WorkResponseDto> {
    try {
      const result = await this.workService.update({
        userId: user.id,
        fields: body,
      });

      return WorkMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof WorkNotFoundException) {
        throw new NotFoundException({
          message: 'Work not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to update work`,
        },
        { cause: err },
      );
    }
  }

  @Delete()
  async remove(
    @User() user: Request['auth']['user'],
  ): Promise<WorkResponseDto> {
    try {
      const result = await this.workService.remove(user.id);

      return WorkMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof WorkNotFoundException) {
        throw new NotFoundException({
          message: 'Work not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to remove work`,
        },
        { cause: err },
      );
    }
  }
}
