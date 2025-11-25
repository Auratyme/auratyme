import { Injectable } from '@nestjs/common';
import { ProfilesRepository } from './profiles.repository';
import { Profile } from './entities';
import { ProfileCreateDto, ProfileUpdateDto } from './dtos';
import { ProfilesMapper } from './profiles.mapper';
import { ProfileNotFoundException } from './exceptions';
import { ProfilesFindOptions } from './types/options/find.type';

@Injectable()
export class ProfilesService {
  constructor(private readonly profilesRepository: ProfilesRepository) {}

  async find(options: ProfilesFindOptions): Promise<Profile[]> {
    const profiles = await this.profilesRepository.find(options);

    return profiles.map((dbProfile) => ProfilesMapper.dbToDomain(dbProfile));
  }

  async findOne(id: string): Promise<Profile> {
    const dbProfile = await this.profilesRepository.findOne(id);

    if (!dbProfile) {
      throw new ProfileNotFoundException(id);
    }

    return ProfilesMapper.dbToDomain(dbProfile);
  }

  async findForUser(id: string): Promise<Profile> {
    const dbProfile = await this.profilesRepository.findOne(id);

    if (!dbProfile) {
      throw new ProfileNotFoundException(id);
    }

    return ProfilesMapper.dbToDomain(dbProfile);
  }

  async create(createDto: ProfileCreateDto): Promise<Profile> {
    const savedDbProfile = await this.profilesRepository.create(createDto);

    return ProfilesMapper.dbToDomain(savedDbProfile);
  }

  async update(updateDto: ProfileUpdateDto): Promise<Profile> {
    const updatedDbProfile = await this.profilesRepository.update(updateDto);

    if (!updatedDbProfile) {
      throw new ProfileNotFoundException(updateDto.userId);
    }

    return ProfilesMapper.dbToDomain(updatedDbProfile);
  }

  async remove(id: string): Promise<Profile> {
    const removedDbProfile = await this.profilesRepository.remove(id);

    if (!removedDbProfile) {
      throw new ProfileNotFoundException(id);
    }

    return ProfilesMapper.dbToDomain(removedDbProfile);
  }
}
