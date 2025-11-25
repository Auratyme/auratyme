import { Injectable } from '@nestjs/common';
import { RoutinesRepository } from './routines.repository';
import { Routine } from './entities';
import { RoutineCreateDto, RoutineUpdateDto } from './dtos';
import { RoutinesMapper } from './routines.mapper';
import { RoutineNotFoundException } from './exceptions';
import { RoutinesFindOptions } from './types/options/find.type';

@Injectable()
export class RoutinesService {
  constructor(private readonly routinesRepository: RoutinesRepository) {}

  async find(options: RoutinesFindOptions): Promise<Routine[]> {
    const routines = await this.routinesRepository.find(options);

    return routines.map((dbRoutine) => RoutinesMapper.dbToDomain(dbRoutine));
  }

  async findOne(id: string): Promise<Routine> {
    const dbRoutine = await this.routinesRepository.findOne(id);

    if (!dbRoutine) {
      throw new RoutineNotFoundException(id);
    }

    return RoutinesMapper.dbToDomain(dbRoutine);
  }

  async create(createDto: RoutineCreateDto): Promise<Routine> {
    const savedDbRoutine = await this.routinesRepository.create(createDto);

    return RoutinesMapper.dbToDomain(savedDbRoutine);
  }

  async update(updateDto: RoutineUpdateDto): Promise<Routine> {
    const updatedDbRoutine = await this.routinesRepository.update(updateDto);

    if (!updatedDbRoutine) {
      throw new RoutineNotFoundException(updateDto.id);
    }

    return RoutinesMapper.dbToDomain(updatedDbRoutine);
  }

  async remove(id: string): Promise<Routine> {
    const removedDbRoutine = await this.routinesRepository.remove(id);

    if (!removedDbRoutine) {
      throw new RoutineNotFoundException(id);
    }

    return RoutinesMapper.dbToDomain(removedDbRoutine);
  }
}
