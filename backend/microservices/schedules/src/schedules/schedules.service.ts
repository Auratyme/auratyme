import { Injectable } from '@nestjs/common';

import { Schedule } from './entities';
import {
  ScheduleCreateDto,
  ScheduleFindOneDto,
  ScheduleRemoveDto,
  SchedulesFindDto,
  ScheduleUpdateDto,
} from './dtos';
import { SchedulesRepository } from './schedules.repository';
import {
  ScheduleCannotBeDeletedException,
  ScheduleNotFoundException,
} from './exceptions';
import { TasksService } from '../tasks/tasks.service';
import { SchedulesMapper } from './schedules.mapper';
import { ForeignKeyViolationException } from 'common';

/**
 * Service for managing schedules.
 */
@Injectable()
export class SchedulesService {
  constructor(
    private readonly schedulesRepository: SchedulesRepository,
    private readonly tasksService: TasksService,
  ) {}

  /**
   * Finds multiple schedules based on the provided options.
   * @param {SchedulesFindManyOptions} options - The options to filter schedules.
   * @returns {Promise<Schedule[]>} A promise that resolves to an array of schedules.
   * @throws {DatabaseException} If there is an error finding schedules.
   */
  async find(findDto: SchedulesFindDto): Promise<Schedule[]> {
    const schedules = await this.schedulesRepository.find(findDto);

    return schedules.map(SchedulesMapper.dbToDomain);
  }

  /**
   * Finds a schedule by ID and user ID.
   * @param {string} id - The ID of the schedule.
   * @param {string} userId - The ID of the user.
   * @returns {Promise<Schedule>} A promise that resolves to the schedule.
   * @throws {ScheduleNotFoundException} If the schedule is not found.
   * @throws {DatabaseException} If there is an error finding the schedule.
   */
  async findOne(findOneDto: ScheduleFindOneDto): Promise<Schedule> {
    const schedule = await this.schedulesRepository.findOne({
      where: { id: findOneDto.where.id, userId: findOneDto.where.userId },
    });

    if (!schedule) {
      throw new ScheduleNotFoundException(findOneDto.where.id);
    }

    return SchedulesMapper.dbToDomain(schedule);
  }

  /**
   * Creates a new schedule.
   * @param {CreateScheduleDto} createDto - The new schedule data.
   * @returns {Promise<Schedule>} A promise that resolves to the created schedule.
   * @throws {DatabaseException} If there is an error creating the schedule.
   */
  async create(createDto: ScheduleCreateDto): Promise<Schedule> {
    const schedule = await this.schedulesRepository.create(createDto);

    return SchedulesMapper.dbToDomain(schedule);
  }

  /**
   * Updates a schedule by ID and user ID.
   * @param {string} id - The ID of the schedule.
   * @param {string} userId - The ID of the user.
   * @param {UpdateScheduleDto} updateDto - The new schedule data.
   * @returns {Promise<Schedule>} A promise that resolves to the updated schedule.
   * @throws {ScheduleNotFoundException} If the schedule is not found.
   * @throws {DatabaseException} If there is an error updating the schedule.
   */
  async update(updateDto: ScheduleUpdateDto): Promise<Schedule> {
    const updatedSchedule = await this.schedulesRepository.update(updateDto);

    if (!updatedSchedule) {
      throw new ScheduleNotFoundException(updateDto.where.id);
    }

    return SchedulesMapper.dbToDomain(updatedSchedule);
  }

  /**
   * Removes a schedule by ID and user ID.
   * @param {string} id - The ID of the schedule.
   * @param {string} userId - The ID of the user.
   * @returns {Promise<void>} A promise that resolves when the schedule is removed.
   * @throws {ScheduleNotFoundException} If the schedule is not found.
   * @throws {DatabaseException} If there is an error removing the schedule.
   */
  async remove(removeDto: ScheduleRemoveDto): Promise<Schedule> {
    const id = removeDto.where.id;
    const userId = removeDto.where.userId;

    try {
      if (removeDto.options?.force === true) {
        const tasks = await this.tasksService.find({
          where: { scheduleId: id },
        });

        for (const task of tasks) {
          await this.tasksService.remove({
            where: { id: task.id, userId },
          });
        }
      }

      const removedSchedule = await this.schedulesRepository.remove({
        where: {
          id: id,
          userId: userId,
        },
      });

      if (!removedSchedule) {
        throw new ScheduleNotFoundException(id);
      }

      return SchedulesMapper.dbToDomain(removedSchedule);
    } catch (err) {
      if (err instanceof ForeignKeyViolationException) {
        throw new ScheduleCannotBeDeletedException(id);
      }

      throw err;
    }
  }
}
