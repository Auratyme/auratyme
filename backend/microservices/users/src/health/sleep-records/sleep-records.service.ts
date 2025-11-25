import { Injectable } from '@nestjs/common';
import { SleepRecordsRepository } from './sleep-records.repository';
import { SleepRecord } from './entities';
import { SleepRecordCreateDto } from './dtos';
import { SleepRecordsMapper } from './sleep-records.mapper';
import { SleepRecordNotFoundException } from './exceptions';
import { SleepRecordsFindOptions } from './types';

@Injectable()
export class SleepRecordsService {
  constructor(
    private readonly sleepRecordsRepository: SleepRecordsRepository,
  ) {}

  async find(options: SleepRecordsFindOptions): Promise<SleepRecord[]> {
    const result = await this.sleepRecordsRepository.find(options);

    return result.map((dbSleepRecord) =>
      SleepRecordsMapper.dbToDomain(dbSleepRecord),
    );
  }

  async findOne(id: string): Promise<SleepRecord> {
    const result = await this.sleepRecordsRepository.findOne(id);

    if (!result) {
      throw new SleepRecordNotFoundException('Sleep record not found.', null);
    }

    return SleepRecordsMapper.dbToDomain(result);
  }

  async create(createDto: SleepRecordCreateDto): Promise<SleepRecord> {
    const result = await this.sleepRecordsRepository.create(createDto);

    return SleepRecordsMapper.dbToDomain(result);
  }

  async remove(id: string): Promise<SleepRecord> {
    const result = await this.sleepRecordsRepository.remove(id);

    if (!result) {
      throw new SleepRecordNotFoundException('Sleep record not found.', null);
    }

    return SleepRecordsMapper.dbToDomain(result);
  }
}
