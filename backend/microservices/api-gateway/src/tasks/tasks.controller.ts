import {
  Body,
  Controller,
  Delete,
  Get,
  HttpStatus,
  InternalServerErrorException,
  Logger,
  NotFoundException,
  Param,
  ParseUUIDPipe,
  Patch,
  Post,
  Query,
  Res,
  Sse,
  UseGuards,
} from '@nestjs/common';
import { TasksService } from './tasks.service';
import { type Response, type Request } from 'express';
import { TaskResponseDto } from './dtos';
import z from 'zod';
import { taskCreateSchema, tasksFindSchema, taskUpdateSchema } from './schemas';
import { TaskNotFoundException } from './exceptions';
import { User } from '../common/decorators';
import { TasksMapper } from './tasks.mapper';
import { AuthGuard } from '../auth/auth.guard';
import { ApiException, ZodValidationPipe } from 'common';
import { SortType } from 'contracts';
import { filter, map, Observable } from 'rxjs';
import { ScheduleNotFoundException } from '../schedules/exceptions';

@UseGuards(AuthGuard)
@Controller({ path: 'tasks', version: '1' })
export class TasksController {
  private readonly logger = new Logger(TasksController.name);

  constructor(private readonly tasksService: TasksService) {}

  @Sse('events')
  events(@User() user: Request['auth']['user']): Observable<unknown> {
    return this.tasksService.events({ userId: user.id }).pipe(
      filter((event) => event.payload.task.userId === user.id),
      map((event) => JSON.stringify(event)),
    );
  }

  @Get()
  async find(
    @Res({ passthrough: true }) res: Response,
    @Query(new ZodValidationPipe(tasksFindSchema))
    query: z.infer<typeof tasksFindSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<TaskResponseDto[]> {
    try {
      const result = await this.tasksService.find({
        options: {
          limit: query.limit,
          orderBy: query.orderBy,
          page: query.page,
          sortBy: query.sortBy === 'asc' ? SortType.ASC : SortType.DESC,
        },
        where: {
          userId: user.id,
        },
      });

      if (result.tasks.length <= 0) {
        res.status(HttpStatus.NO_CONTENT);
        return [];
      }

      return result.tasks.map((task) => TasksMapper.clientToResponseDto(task));
    } catch (err) {
      throw new InternalServerErrorException(
        new ApiException(
          HttpStatus.INTERNAL_SERVER_ERROR,
          'Failed to find tasks',
        ),
        { cause: err },
      );
    }
  }

  @Get(':id')
  async findOne(
    @Param('id', ParseUUIDPipe) id: string,
    @User() user: Request['auth']['user'],
  ): Promise<TaskResponseDto> {
    try {
      const task = await this.tasksService.findOne({
        where: { id, userId: user.id },
      });

      return TasksMapper.clientToResponseDto(task);
    } catch (err) {
      if (err instanceof TaskNotFoundException) {
        throw new NotFoundException(
          new ApiException(HttpStatus.NOT_FOUND, 'task not found'),
        );
      }

      throw new InternalServerErrorException(
        new ApiException(
          HttpStatus.INTERNAL_SERVER_ERROR,
          'Failed to find one task',
        ),
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(taskCreateSchema))
    body: z.infer<typeof taskCreateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<TaskResponseDto> {
    try {
      const createdTask = await this.tasksService.create({
        ...body,
        description: body.description || '',
        dueTo: body.dueTo || '',
        repeat: body.repeat || '',
        status: TasksMapper.domainToClientStatus(body.status),
        userId: user.id,
      });

      return TasksMapper.clientToResponseDto(createdTask);
    } catch (err) {
      if (err instanceof ScheduleNotFoundException) {
        throw new NotFoundException(
          new ApiException(HttpStatus.NOT_FOUND, 'schedule not found'),
        );
      }

      throw new InternalServerErrorException(
        new ApiException(
          HttpStatus.INTERNAL_SERVER_ERROR,
          'Failed to create task',
        ),
        { cause: err },
      );
    }
  }

  @Patch(':id')
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body(new ZodValidationPipe(taskUpdateSchema))
    body: z.infer<typeof taskUpdateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<TaskResponseDto> {
    try {
      const updatedTask = await this.tasksService.update({
        where: { id, userId: user.id },
        fields: {
          ...body,
          status: body?.status
            ? TasksMapper.domainToClientStatus(body.status)
            : undefined,
          description: body?.description === null ? '' : body?.description,
          dueTo: body?.dueTo === null ? '' : body?.dueTo,
          repeat: body?.repeat === null ? '' : body?.repeat,
        },
      });

      return TasksMapper.clientToResponseDto(updatedTask);
    } catch (err) {
      if (err instanceof TaskNotFoundException) {
        throw new NotFoundException(
          new ApiException(HttpStatus.NOT_FOUND, 'task not found'),
        );
      }

      if (err instanceof ScheduleNotFoundException) {
        throw new NotFoundException(
          new ApiException(HttpStatus.NOT_FOUND, 'schedule not found'),
        );
      }

      throw new InternalServerErrorException(
        new ApiException(
          HttpStatus.INTERNAL_SERVER_ERROR,
          'Failed to update task',
        ),
        { cause: err },
      );
    }
  }

  @Delete(':id')
  async remove(
    @Param('id', ParseUUIDPipe) id: string,
    @User() user: Request['auth']['user'],
  ): Promise<TaskResponseDto> {
    try {
      const removedTask = await this.tasksService.remove({
        where: { id, userId: user.id },
      });

      return TasksMapper.clientToResponseDto(removedTask);
    } catch (err) {
      if (err instanceof TaskNotFoundException) {
        throw new NotFoundException(
          new ApiException(HttpStatus.NOT_FOUND, 'task not found'),
        );
      }

      throw new InternalServerErrorException(
        new ApiException(
          HttpStatus.INTERNAL_SERVER_ERROR,
          'Failed to remove task',
        ),
        { cause: err },
      );
    }
  }
}
