import { Injectable } from '@nestjs/common';
import { UsersRepository } from './users.repository';
import { User } from './entities';
import {
  UserCreateDto,
  UserFindOneDto,
  UserRemoveDto,
  UsersFindDto,
  UserUpdateDto,
} from './dtos';
import { UsersMapper } from './users.mapper';
import { UserNotFoundException } from './exceptions';

@Injectable()
export class UsersService {
  constructor(private readonly usersRepository: UsersRepository) {}

  async find(dto: UsersFindDto): Promise<User[]> {
    const users = await this.usersRepository.find(dto.options);

    return users.map((dbUser) => UsersMapper.dbToDomain(dbUser));
  }

  async findOne(dto: UserFindOneDto): Promise<User> {
    const dbUser = await this.usersRepository.findOne(dto);

    if (!dbUser) {
      throw new UserNotFoundException(dto.where.id);
    }

    return UsersMapper.dbToDomain(dbUser);
  }

  async create(dto: UserCreateDto): Promise<User> {
    const savedDbUser = await this.usersRepository.create(dto);

    return UsersMapper.dbToDomain(savedDbUser);
  }

  async update(dto: UserUpdateDto): Promise<User> {
    const updatedDbUser = await this.usersRepository.update(dto);

    if (!updatedDbUser) {
      throw new UserNotFoundException(dto.where.id);
    }

    return UsersMapper.dbToDomain(updatedDbUser);
  }

  async remove(dto: UserRemoveDto): Promise<User> {
    const removedDbUser = await this.usersRepository.remove(dto);

    if (!removedDbUser) {
      throw new UserNotFoundException(dto.where.id);
    }

    return UsersMapper.dbToDomain(removedDbUser);
  }
}
