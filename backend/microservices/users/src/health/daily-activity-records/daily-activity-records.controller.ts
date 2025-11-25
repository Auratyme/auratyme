import { User } from '@app/common/decorators';
import {
  Controller,
  Get,
  Post,
  Delete,
  Res,
  Query,
  HttpStatus,
  InternalServerErrorException,
  Param,
  ParseUUIDPipe,
  NotFoundException,
  Body,
  UseGuards,
} from '@nestjs/common';
import { Request, Response } from 'express';
import z from 'zod';
import {
  dailyActivityRecordCreateSchema,
  dailyActivityRecordsFindSchema,
} from './schemas';
import { ZodValidationPipe } from '@app/common/pipes';
import { DailyActivityRecordResponseDto } from './dtos';
import { DailyActivityRecordsService } from './daily-activity-records.service';
import { DailyActivityRecordsMapper } from './daily-activity-records.mapper';
import { DailyActivityRecordNotFoundException } from './exceptions';
import { AuthGuard } from '@app/auth/auth.guard';

@UseGuards(AuthGuard)
@Controller({ path: 'daily-activity-records', version: '1' })
export class DailyActivityRecordsController {
  constructor(
    private readonly dailyActivityRecordsService: DailyActivityRecordsService,
  ) {}

  @Get()
  async find(
    @User() user: Request['auth']['user'],
    @Res({ passthrough: true }) res: Response,
    @Query(new ZodValidationPipe(dailyActivityRecordsFindSchema))
    query: z.infer<typeof dailyActivityRecordsFindSchema>,
  ): Promise<DailyActivityRecordResponseDto[]> {
    try {
      const result = await this.dailyActivityRecordsService.find({
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

      return result.map((dailyActivityRecord) =>
        DailyActivityRecordsMapper.domainToResponseDto(dailyActivityRecord),
      );
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: 'Failed to retrieve daily activity records',
        },
        {
          cause: err,
        },
      );
    }
  }

  @Get(':id')
  async findOne(
    @Param('id', ParseUUIDPipe) id: string,
  ): Promise<DailyActivityRecordResponseDto> {
    try {
      const result = await this.dailyActivityRecordsService.findOne(id);

      return DailyActivityRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof DailyActivityRecordNotFoundException) {
        throw new NotFoundException({
          message: 'Daily activity record not found!',
        });
      }

      throw new InternalServerErrorException(
        {
          message: 'Failed to find one daily activity record',
        },
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(dailyActivityRecordCreateSchema))
    body: z.infer<typeof dailyActivityRecordCreateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<DailyActivityRecordResponseDto> {
    try {
      const result = await this.dailyActivityRecordsService.create({
        date: body.date,
        steps: body.steps,
        userId: user.id,
      });

      return DailyActivityRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: 'Failed to create daily activity record',
        },
        { cause: err },
      );
    }
  }

  @Delete(':id')
  async remove(
    @Param('id', ParseUUIDPipe) id: string,
  ): Promise<DailyActivityRecordResponseDto> {
    try {
      const result = await this.dailyActivityRecordsService.remove(id);

      return DailyActivityRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof DailyActivityRecordNotFoundException) {
        throw new NotFoundException({
          message: 'Daily activity record not found!',
        });
      }

      throw new InternalServerErrorException(
        {
          message: 'Failed to remove daily activity record',
        },
        { cause: err },
      );
    }
  }
}
