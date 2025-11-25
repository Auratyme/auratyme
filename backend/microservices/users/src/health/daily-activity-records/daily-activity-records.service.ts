import { Injectable } from '@nestjs/common';
import { DailyActivityRecordsRepository } from './daily-activity-records.respository';
import { DailyActivityRecord } from './entities';
import { DailyActivityRecordCreateDto } from './dtos';
import { DailyActivityRecordsMapper } from './daily-activity-records.mapper';
import { DailyActivityRecordNotFoundException } from './exceptions';
import { DailyActivityRecordsFindOptions } from './types';

@Injectable()
export class DailyActivityRecordsService {
  constructor(
    private readonly dailyActivityRecordsRepository: DailyActivityRecordsRepository,
  ) {}

  async find(
    options: DailyActivityRecordsFindOptions,
  ): Promise<DailyActivityRecord[]> {
    const result = await this.dailyActivityRecordsRepository.find(options);

    return result.map((dbDailyActivityRecord) =>
      DailyActivityRecordsMapper.dbToDomain(dbDailyActivityRecord),
    );
  }

  async findOne(id: string): Promise<DailyActivityRecord> {
    const result = await this.dailyActivityRecordsRepository.findOne(id);

    if (!result) {
      throw new DailyActivityRecordNotFoundException(
        'Daily activity record not found.',
        null,
      );
    }

    return DailyActivityRecordsMapper.dbToDomain(result);
  }

  async create(
    createDto: DailyActivityRecordCreateDto,
  ): Promise<DailyActivityRecord> {
    const result = await this.dailyActivityRecordsRepository.create(createDto);

    return DailyActivityRecordsMapper.dbToDomain(result);
  }

  async remove(id: string): Promise<DailyActivityRecord> {
    const result = await this.dailyActivityRecordsRepository.remove(id);

    if (!result) {
      throw new DailyActivityRecordNotFoundException(
        'Daily activity record not found.',
        null,
      );
    }

    return DailyActivityRecordsMapper.dbToDomain(result);
  }
}
