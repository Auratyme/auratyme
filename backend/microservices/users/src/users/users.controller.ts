import { Controller, Logger } from '@nestjs/common';
import { UsersService } from './users.service';
import { GrpcMethod, Payload } from '@nestjs/microservices';
import { SchedulesConfig, User, UsersFindResponse } from 'contracts';
import { z } from 'zod';
import {
  usersFindSchema,
  userFindOneSchema,
  userCreateSchema,
  userRemoveSchema,
  userUpdateSchema,
} from './schemas';
import { GrpcInternalException, GrpcNotFoundException } from 'common';
import { UserNotFoundException } from './exceptions';
import { UsersMapper } from './users.mapper';

@Controller()
export class UsersController {
  private readonly logger = new Logger(UsersController.name);

  constructor(private readonly usersService: UsersService) {}

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.FIND_METHOD)
  async find(
    @Payload() payload: z.infer<typeof usersFindSchema>,
  ): Promise<UsersFindResponse> {
    try {
      const users = await this.usersService.find(
        UsersMapper.findRequestToDto(payload),
      );

      return {
        users: users,
      };
    } catch (err) {
      throw new GrpcInternalException(
        'unknown error occured while finding users',
        null,
        err,
      );
    }
  }

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.FIND_ONE_METHOD)
  async findOne(
    @Payload() payload: z.infer<typeof userFindOneSchema>,
  ): Promise<User> {
    try {
      const user = await this.usersService.findOne(payload);

      return user;
    } catch (err) {
      if (err instanceof UserNotFoundException) {
        throw new GrpcNotFoundException('user not found', null);
      }

      throw new GrpcInternalException(
        'unknown error occured while finding one user',
        null,
        err,
      );
    }
  }

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.CREATE_METHOD)
  async create(
    @Payload() payload: z.infer<typeof userCreateSchema>,
  ): Promise<User> {
    try {
      const createdUser = await this.usersService.create(payload);

      return createdUser;
    } catch (err) {
      throw new GrpcInternalException(
        'unknown error occured while creating user',
        null,
        err,
      );
    }
  }

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.UPDATE_METHOD)
  async update(
    @Payload() payload: z.infer<typeof userUpdateSchema>,
  ): Promise<User> {
    try {
      const updatedUser = await this.usersService.update(payload);

      return updatedUser;
    } catch (err) {
      if (err instanceof UserNotFoundException) {
        throw new GrpcNotFoundException('user not found', null);
      }

      throw new GrpcInternalException(
        'unknown error occured while updating user',
        null,
        err,
      );
    }
  }

  @GrpcMethod(SchedulesConfig.SERVICE_NAME, SchedulesConfig.REMOVE_METHOD)
  async remove(
    @Payload() payload: z.infer<typeof userRemoveSchema>,
  ): Promise<User> {
    try {
      const removedUser = await this.usersService.remove(payload);

      return removedUser;
    } catch (err) {
      if (err instanceof UserNotFoundException) {
        throw new GrpcNotFoundException('user not found', null);
      }

      throw new GrpcInternalException(
        'unknown error occured while removing user',
        null,
        err,
      );
    }
  }
}
