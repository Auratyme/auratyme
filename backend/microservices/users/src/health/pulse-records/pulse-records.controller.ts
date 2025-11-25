import {
  Controller,
  Delete,
  Get,
  HttpStatus,
  InternalServerErrorException,
  Param,
  ParseUUIDPipe,
  Post,
  Res,
  UseGuards,
  NotFoundException,
  Body,
  Query,
} from '@nestjs/common';
import { PulseRecordResponseDto } from './dtos';
import { PulseRecordsService } from './pulse-records.service';
import { AuthGuard } from '@app/auth/auth.guard';
import { User } from '@app/common/decorators';
import { Request, Response } from 'express';
import { PulseRecordNotFoundException } from './exceptions';
import { PulseRecordsMapper } from './pulse-records.mapper';
import z from 'zod';
import { pulseRecordCreateSchema } from './schemas';
import { ZodValidationPipe } from '@app/common/pipes';
import { pulseRecordsFindSchema } from './schemas/find.schema';

@UseGuards(AuthGuard)
@Controller({ path: 'pulse-records', version: '1' })
export class PulseRecordsController {
  constructor(private readonly pulseRecordsService: PulseRecordsService) {}

  @Get()
  async find(
    @User() user: Request['auth']['user'],
    @Res({ passthrough: true }) res: Response,
    @Query(new ZodValidationPipe(pulseRecordsFindSchema))
    query: z.infer<typeof pulseRecordsFindSchema>,
  ): Promise<PulseRecordResponseDto[]> {
    try {
      const result = await this.pulseRecordsService.find({
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

      return result.map((pulseRecord) =>
        PulseRecordsMapper.domainToResponseDto(pulseRecord),
      );
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: 'Failed to retrieve pulse records',
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
  ): Promise<PulseRecordResponseDto> {
    try {
      const result = await this.pulseRecordsService.findOne(id);

      return PulseRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof PulseRecordNotFoundException) {
        throw new NotFoundException({ message: 'Pulse record not found!' });
      }

      throw new InternalServerErrorException(
        {
          message: 'Failed to find one pulse record',
        },
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(pulseRecordCreateSchema))
    body: z.infer<typeof pulseRecordCreateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<PulseRecordResponseDto> {
    try {
      const result = await this.pulseRecordsService.create({
        pulse: body.pulse,
        timestamp: body.timestamp,
        userId: user.id,
      });

      return PulseRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: 'Failed to create pulse record',
        },
        { cause: err },
      );
    }
  }

  @Delete(':id')
  async remove(
    @Param('id', ParseUUIDPipe) id: string,
  ): Promise<PulseRecordResponseDto> {
    try {
      const result = await this.pulseRecordsService.remove(id);

      return PulseRecordsMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof PulseRecordNotFoundException) {
        throw new NotFoundException({ message: 'Pulse record not found!' });
      }

      throw new InternalServerErrorException(
        {
          message: 'Failed to remove pulse record',
        },
        { cause: err },
      );
    }
  }
}
