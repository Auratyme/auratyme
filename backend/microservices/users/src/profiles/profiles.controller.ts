import {
  Body,
  Controller,
  Delete,
  Get,
  InternalServerErrorException,
  NotFoundException,
  Patch,
  Post,
  UseGuards,
} from '@nestjs/common';

import { ProfilesService } from './profiles.service';
import { ProfileResponseDto } from './dtos';
import { ProfilesMapper } from './profiles.mapper';
import { ProfileNotFoundException } from './exceptions';
import { Request } from 'express';
import { ZodValidationPipe } from '@app/common/pipes';
import { profileCreateSchema, profilesUpdateSchema } from './schemas';
import { AuthGuard } from '@app/auth/auth.guard';
import { User } from '@app/common/decorators';
import z from 'zod';

@UseGuards(AuthGuard)
@Controller({ path: 'profile', version: '1' })
export class ProfilesController {
  constructor(private readonly profilesService: ProfilesService) {}

  @Get()
  async find(
    @User() user: Request['auth']['user'],
  ): Promise<ProfileResponseDto> {
    try {
      const result = await this.profilesService.findForUser(user.id);

      return ProfilesMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof ProfileNotFoundException) {
        throw new NotFoundException({
          message: 'Profile not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: 'Failed to retrieve profiles',
        },
        { cause: err },
      );
    }
  }

  @Post()
  async create(
    @Body(new ZodValidationPipe(profileCreateSchema))
    body: z.infer<typeof profileCreateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<ProfileResponseDto> {
    try {
      const result = await this.profilesService.create({
        userId: user.id,
        birthDate: body.birthDate,
        chronotypeMEQ: body.chronotypeMEQ,
      });

      return ProfilesMapper.domainToResponseDto(result);
    } catch (err) {
      throw new InternalServerErrorException(
        {
          message: `Failed to create profile`,
        },
        { cause: err },
      );
    }
  }

  @Patch()
  async update(
    @Body(new ZodValidationPipe(profilesUpdateSchema))
    body: z.infer<typeof profilesUpdateSchema>,
    @User() user: Request['auth']['user'],
  ): Promise<ProfileResponseDto> {
    try {
      const result = await this.profilesService.update({
        userId: user.id,
        fields: body,
      });

      return ProfilesMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof ProfileNotFoundException) {
        throw new NotFoundException({
          message: 'Profile not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to update profile`,
        },
        { cause: err },
      );
    }
  }

  @Delete()
  async remove(
    @User() user: Request['auth']['user'],
  ): Promise<ProfileResponseDto> {
    try {
      const result = await this.profilesService.remove(user.id);

      return ProfilesMapper.domainToResponseDto(result);
    } catch (err) {
      if (err instanceof ProfileNotFoundException) {
        throw new NotFoundException({
          message: 'Profile not found.',
        });
      }

      throw new InternalServerErrorException(
        {
          message: `Failed to remove profile`,
        },
        { cause: err },
      );
    }
  }
}
