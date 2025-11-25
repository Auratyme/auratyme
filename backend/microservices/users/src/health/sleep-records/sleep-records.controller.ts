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
import { sleepRecordCreateSchema, sleepRecordsFindSchema } from './schemas';
import { ZodValidationPipe } from '@app/common/pipes';
import { SleepRecordResponseDto } from './dtos';
import { SleepRecordsService } from './sleep-records.service';
import { SleepRecordsMapper } from './sleep-records.mapper';
import { SleepRecordNotFoundException } from './exceptions';
import { AuthGuard } from '@app/auth/auth.guard';

@UseGuards(AuthGuard)
@Controller({ path: 'sleep-records', version: '1' })
export class SleepRecordsController {
  constructor(private readonly sleepRecordsService: SleepRecordsService) {}

  @Get()
  async find(
    @User() user: Request['auth']['user'],
    @Res({ passthrough: true }) res: Response,
    @Query(new ZodValidationPipe(sleepRecordsFindSchema))
    query: z.infer<typeof sleepRecordsFindSchema>,
  ): Promise<SleepRecordResponseDto[]> {
    try {
      const result = await this.sleepRecordsService.find({
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

      return result.map((sleepRecord) =>
        SleepRecordsMapper.domainToResponseDto(sleepRecord),
      );
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: 'Failed to retrieve sleep records',
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
  ): Promise<SleepRecordResponseDto> {
    try {
      const result = await this.sleepRecordsService.findOne(id);

      return SleepRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof SleepRecordNotFoundException) {
        throw new NotFoundException({
          message: 'Sleep record not found!',
        });
      }

      throw new InternalServerErrorException(
        {
          message: 'Failed to find one sleep record',
        },
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(sleepRecordCreateSchema))
    body: z.infer<typeof sleepRecordCreateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<SleepRecordResponseDto> {
    try {
      const result = await this.sleepRecordsService.create({
        endTime: body.endTime,
        startTime: body.startTime,
        phase: body.phase,
        userId: user.id,
      });

      return SleepRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: 'Failed to create sleep record',
        },
        { cause: err },
      );
    }
  }

  @Delete(':id')
  async remove(
    @Param('id', ParseUUIDPipe) id: string,
  ): Promise<SleepRecordResponseDto> {
    try {
      const result = await this.sleepRecordsService.remove(id);

      return SleepRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof SleepRecordNotFoundException) {
        throw new NotFoundException({
          message: 'Sleep record not found!',
        });
      }

      throw new InternalServerErrorException(
        {
          message: 'Failed to remove sleep record',
        },
        { cause: err },
      );
    }
  }
}
