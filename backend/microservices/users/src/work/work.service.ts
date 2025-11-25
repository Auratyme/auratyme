import { Injectable } from '@nestjs/common';
import { WorkRepository } from './work.repository';
import { Work } from './entities';
import { WorkCreateDto, WorkUpdateDto } from './dtos';
import { WorkMapper } from './work.mapper';
import { WorkNotFoundException } from './exceptions';

@Injectable()
export class WorkService {
  constructor(private readonly workRepository: WorkRepository) {}

  async findForUser(userId: string): Promise<Work> {
    const work = await this.workRepository.findForUser(userId);

    if (!work) {
      throw new WorkNotFoundException(userId);
    }

    return WorkMapper.dbToDomain(work);
  }

  async create(createDto: WorkCreateDto): Promise<Work> {
    const savedDbWork = await this.workRepository.create(createDto);

    return WorkMapper.dbToDomain(savedDbWork);
  }

  async update(updateDto: WorkUpdateDto): Promise<Work> {
    const updatedDbWork = await this.workRepository.update(updateDto);

    if (!updatedDbWork) {
      throw new WorkNotFoundException(updateDto.userId);
    }

    return WorkMapper.dbToDomain(updatedDbWork);
  }

  async remove(userId: string): Promise<Work> {
    const removedDbWork = await this.workRepository.remove(userId);

    if (!removedDbWork) {
      throw new WorkNotFoundException(userId);
    }

    return WorkMapper.dbToDomain(removedDbWork);
  }
}
