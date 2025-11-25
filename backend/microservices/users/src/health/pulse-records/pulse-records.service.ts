import { Injectable } from '@nestjs/common';
import { PulseRecordsRepository } from './pulse-records.repository';
import { PulseRecord } from './entities';
import { PulseRecordCreateDto } from './dtos';
import { PulseRecordsMapper } from './pulse-records.mapper';
import { PulseRecordNotFoundException } from './exceptions';
import { PulseRecordsFindOptions } from './types';

@Injectable()
export class PulseRecordsService {
  constructor(
    private readonly pulseRecordsRepository: PulseRecordsRepository,
  ) {}

  async find(options: PulseRecordsFindOptions): Promise<PulseRecord[]> {
    const result = await this.pulseRecordsRepository.find(options);

    return result.map((dbPulseRecord) =>
      PulseRecordsMapper.dbToDomain(dbPulseRecord),
    );
  }

  async findOne(id: string): Promise<PulseRecord> {
    const result = await this.pulseRecordsRepository.findOne(id);

    if (!result) {
      throw new PulseRecordNotFoundException('Pulse record not found.', null);
    }

    return PulseRecordsMapper.dbToDomain(result);
  }

  async create(createDto: PulseRecordCreateDto): Promise<PulseRecord> {
    const result = await this.pulseRecordsRepository.create(createDto);

    return PulseRecordsMapper.dbToDomain(result);
  }

  async remove(id: string): Promise<PulseRecord> {
    const result = await this.pulseRecordsRepository.remove(id);

    if (!result) {
      throw new PulseRecordNotFoundException('Pulse record not found.', null);
    }

    return PulseRecordsMapper.dbToDomain(result);
  }
}
