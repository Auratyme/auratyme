import {
  Body,
  ConflictException,
  Controller,
  Delete,
  Get,
  HttpStatus,
  InternalServerErrorException,
  Logger,
  NotFoundException,
  Param,
  ParseUUIDPipe,
  Patch,
  Post,
  Query,
  Res,
  UseGuards,
} from '@nestjs/common';
import { SchedulesService } from './schedules.service';
import { type Response, type Request } from 'express';
import { ScheduleResponseDto } from './dtos';
import z from 'zod';
import {
  scheduleCreateSchema,
  scheduleRemoveSchema,
  schedulesFindSchema,
  scheduleUpdateSchema,
} from './schemas';
import {
  ScheduleCannotBeDeletedException,
  ScheduleNotFoundException,
} from './exceptions';
import { User } from '../common/decorators';
import { SchedulesMapper } from './schedules.mapper';
import { AuthGuard } from '../auth/auth.guard';
import { ZodValidationPipe } from 'common';
import { SortType } from 'contracts';

@UseGuards(AuthGuard)
@Controller({ path: 'schedules', version: '1' })
export class SchedulesController {
  private readonly logger = new Logger(SchedulesController.name);

  constructor(private readonly schedulesService: SchedulesService) {}

  @Get()
  async find(
    @Res({ passthrough: true }) res: Response,
    @Query(new ZodValidationPipe(schedulesFindSchema))
    query: z.infer<typeof schedulesFindSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<ScheduleResponseDto[]> {
    try {
      const result = await this.schedulesService.find({
        options: {
          limit: query.limit,
          orderBy: query.orderBy,
          page: query.page,
          sortBy: query.sortBy === 'asc' ? SortType.ASC : SortType.DESC,
        },
        where: {
          userId: user.id,
        },
      });

      if (result.schedules.length <= 0) {
        res.status(HttpStatus.NO_CONTENT);
        return [];
      }

      return result.schedules.map((schedule) =>
        SchedulesMapper.clientToResponseDto(schedule),
      );
    } catch (err) {
      throw new InternalServerErrorException(
        { message: 'Failed to find schedule' },
        { cause: err },
      );
    }
  }

  @Get(':id')
  async findOne(
    @Param('id', ParseUUIDPipe) id: string,
    @User() user: Request['auth']['user'],
  ): Promise<ScheduleResponseDto> {
    try {
      const schedule = await this.schedulesService.findOne({
        where: { id, userId: user.id },
      });

      return SchedulesMapper.clientToResponseDto(schedule);
    } catch (err) {
      if (err instanceof ScheduleNotFoundException) {
        throw new NotFoundException({ message: 'Schedule not found!' });
      }

      throw new InternalServerErrorException(
        { message: 'Failed to remove schedule' },
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(scheduleCreateSchema))
    body: z.infer<typeof scheduleCreateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<ScheduleResponseDto> {
    try {
      const createdSchedule = await this.schedulesService.create({
        description: body.description === null ? '' : body.description,
        name: body.name,
        userId: user.id,
      });

      return SchedulesMapper.clientToResponseDto(createdSchedule);
    } catch (err) {
      throw new InternalServerErrorException(
        { message: 'Failed to remove schedule' },
        { cause: err },
      );
    }
  }

  @Patch(':id')
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body(new ZodValidationPipe(scheduleUpdateSchema))
    body: z.infer<typeof scheduleUpdateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<ScheduleResponseDto> {
    try {
      const updatedSchedule = await this.schedulesService.update({
        where: { id, userId: user.id },
        fields: {
          description: body?.description === null ? '' : body?.description,
          name: body?.name,
        },
      });

      return SchedulesMapper.clientToResponseDto(updatedSchedule);
    } catch (err) {
      if (err instanceof ScheduleNotFoundException) {
        throw new NotFoundException({ message: 'Schedule not found!' });
      }

      throw new InternalServerErrorException(
        { message: 'Failed to remove schedule' },
        { cause: err },
      );
    }
  }

  @Delete(':id')
  async remove(
    @Param('id', ParseUUIDPipe) id: string,
    @Body(new ZodValidationPipe(scheduleRemoveSchema))
    body: z.infer<typeof scheduleRemoveSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<ScheduleResponseDto> {
    try {
      const removedSchedule = await this.schedulesService.remove({
        where: { id, userId: user.id },
        options: {
          force: body?.force,
        },
      });

      return SchedulesMapper.clientToResponseDto(removedSchedule);
    } catch (err) {
      if (err instanceof ScheduleNotFoundException) {
        throw new NotFoundException({ message: 'Schedule not found!' });
      }

      if (err instanceof ScheduleCannotBeDeletedException) {
        throw new ConflictException({
          message: 'Schedule cannot be deleted, because it has tasks',
        });
      }

      throw new InternalServerErrorException(
        { message: 'Failed to remove schedule' },
        { cause: err },
      );
    }
  }
}
