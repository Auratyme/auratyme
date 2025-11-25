import { Injectable, Logger } from '@nestjs/common';

import { BrokerTask } from '@app/common/enums';
import { TaskJobPayload, TasksFindOptions } from './types';
import { TasksRepository } from './tasks.repository';
import { TaskEvent } from './enums';
import { ScheduleNotFoundException } from '../schedules/exceptions';
import { TaskNotFoundException } from './exceptions';
import { Task } from './entities';
import {
  TaskCreateDto,
  TaskFindOneDto,
  TaskRemoveDto,
  TasksFindDto,
  TaskUpdateDto,
} from './dtos';
import { JobsService } from '../jobs/jobs.service';
import { SchedulesRepository } from '../schedules/schedules.repository';
import { TasksMapper } from './tasks.mapper';
import { JobType } from '../jobs/enums';

@Injectable()
export class TasksService {
  private readonly logger = new Logger(TasksService.name);

  constructor(
    private readonly tasksRepository: TasksRepository,
    private readonly schedulesRepository: SchedulesRepository,
    private readonly jobsService: JobsService<TaskJobPayload>,
  ) {}

  /**
   * Finds multiple tasks based on the provided options.
   * @param {TasksFindOptions} options - The options to filter tasks.
   * @returns {Promise<Task[]>} A promise that resolves to an array of tasks.
   * @throws {DatabaseException} If there is an error finding tasks.
   */
  async find(findDto: TasksFindDto): Promise<Task[]> {
    const dbTasks = await this.tasksRepository.find(findDto);

    return dbTasks.map((dbTask) => TasksMapper.dbToDomain(dbTask));
  }
  /**
   * Finds a task by ID and user ID.
   * @param {string} id - The ID of the task.
   * @param {string} userId - The ID of the user.
   * @returns {Promise<Task>} A promise that resolves to the task.
   * @throws {TaskNotFoundException} If the task is not found.
   * @throws {DatabaseException} If there is an error finding the task.
   */
  async findOne(findOneDto: TaskFindOneDto): Promise<Task> {
    const { id, userId } = findOneDto.where;

    const dbTask = await this.tasksRepository.findOne({
      where: { id, userId },
    });

    if (!dbTask) {
      throw new TaskNotFoundException(id);
    }

    return TasksMapper.dbToDomain(dbTask);
  }

  /**
   * Creates a new task.
   * @param {CreateTaskDto} newTask - The new task data.
   * @returns {Promise<Task>} A promise that resolves to the created task.
   * @throws {DatabaseException} If there is an error creating the task.
   */
  async create(createDto: TaskCreateDto): Promise<Task> {
    const dbSchedule = await this.schedulesRepository.findOne({
      where: { id: createDto.scheduleId },
    });

    if (!dbSchedule) {
      throw new ScheduleNotFoundException(createDto.scheduleId);
    }

    const dbTask = await this.tasksRepository.create({
      ...createDto,
      dueTo: createDto.dueTo ? new Date(createDto.dueTo) : null,
    });

    if (dbTask.dueTo) {
      await this.jobsService.scheduleSingle(
        {
          ackEventName: TaskEvent.DUE,
          executionDate: dbTask.dueTo.toISOString(),
          name: BrokerTask.SCHEDULE_SINGLE_JOB,
          payload: {
            taskId: dbTask.id,
            taskName: dbTask.name,
            userId: dbTask.userId,
          },
        },
        dbTask.id,
      );
    }

    if (dbTask.repeat) {
      await this.jobsService.scheduleCron(
        {
          ackEventName: TaskEvent.REPEATED,
          cron: dbTask.repeat,
          name: BrokerTask.SCHEDULE_CRON_JOB,
          payload: {
            taskId: dbTask.id,
            taskName: dbTask.name,
            userId: dbTask.userId,
          },
        },
        dbTask.id,
      );
    }

    return TasksMapper.dbToDomain(dbTask);
  }

  /**
   * Updates a task by ID and user ID.
   * @param {string} id - The ID of the task.
   * @param {string} userId - The ID of the user.
   * @param {UpdateTaskDto} newTask - The new task data.
   * @returns {Promise<Task>} A promise that resolves to the updated task.
   * @throws {TaskNotFoundException} If the task is not found.
   * @throws {DatabaseException} If there is an error updating the task.
   */
  async update(updateDto: TaskUpdateDto): Promise<Task> {
    const { id, userId } = updateDto.where;
    const fields = updateDto.fields;

    if (fields?.scheduleId) {
      const dbSchedule = await this.schedulesRepository.findOne({
        where: { id: fields?.scheduleId },
      });

      if (!dbSchedule) {
        throw new ScheduleNotFoundException(fields?.scheduleId);
      }
    }

    const updatedTask = await this.tasksRepository.update({
      where: { id, userId },
      fields: {
        description: fields?.description,
        dueTo: fields?.dueTo ? new Date(fields?.dueTo) : undefined,
        name: fields?.name,
        repeat: fields?.repeat,
        scheduleId: fields?.scheduleId,
        status: fields?.status,
      },
    });

    if (!updatedTask) {
      throw new TaskNotFoundException(id);
    }

    const jobs = await this.jobsService.findByTaskId(id);

    if (fields?.dueTo) {
      const job = jobs.find((job) => {
        return job.type === JobType.SINGLE;
      });

      if (!job) {
        await this.jobsService.scheduleSingle(
          {
            ackEventName: TaskEvent.DUE,
            executionDate: fields?.dueTo,
            name: BrokerTask.SCHEDULE_SINGLE_JOB,
            payload: {
              userId: updatedTask.userId,
              taskId: id,
              taskName: updatedTask.name,
            },
          },
          id,
        );
      } else {
        await this.jobsService.rescheduleSingle({
          executionDate: fields?.dueTo,
          id: job.id,
        });
      }
    }

    if (fields?.dueTo === null) {
      const job = jobs.find((job) => {
        return job.type === JobType.SINGLE;
      });

      if (job) {
        await this.jobsService.unscheduleSingle({
          id: job.id,
        });
      }
    }

    if (fields?.repeat) {
      const job = jobs.find((job) => {
        return job.type === JobType.CRON;
      });

      if (!job) {
        await this.jobsService.scheduleCron(
          {
            ackEventName: TaskEvent.REPEATED,
            cron: fields?.repeat,
            name: BrokerTask.SCHEDULE_CRON_JOB,
            payload: {
              userId: updatedTask.userId,
              taskId: id,
              taskName: updatedTask.name,
            },
          },
          id,
        );
      } else {
        await this.jobsService.rescheduleCron({
          cron: fields?.repeat,
          id: job.id,
        });
      }
    }

    if (fields?.repeat === null) {
      const job = jobs.find((job) => {
        return job.type === JobType.CRON;
      });

      if (job) {
        await this.jobsService.unscheduleCron({ id: job.id });
      }
    }

    return TasksMapper.dbToDomain(updatedTask);
  }

  /**
   * Removes a task by ID and user ID.
   * @param {string} id - The ID of the task.
   * @param {string} userId - The ID of the user.
   * @returns {Promise<void>} A promise that resolves when the task is removed.
   * @throws {TaskNotFoundException} If the task is not found.
   * @throws {DatabaseException} If there is an error removing the task.
   */
  async remove(removeDto: TaskRemoveDto): Promise<Task> {
    const { id, userId } = removeDto.where;

    const task = await this.tasksRepository.findOne({
      where: { id, userId },
    });

    if (!task) {
      throw new TaskNotFoundException(id);
    }

    const jobs = await this.jobsService.findByTaskId(id);

    if (task.dueTo) {
      const job = jobs.find((job) => {
        return job.type === JobType.SINGLE;
      });

      if (job) {
        await this.jobsService.unscheduleSingle({ id: job.id });
      }
    }

    if (task.repeat) {
      const job = jobs.find((job) => {
        return job.type === JobType.CRON;
      });

      if (job) {
        await this.jobsService.unscheduleCron({ id: job.id });
      }
    }

    await this.tasksRepository.remove({
      where: { id, userId },
    });

    return TasksMapper.dbToDomain(task);
  }
}
