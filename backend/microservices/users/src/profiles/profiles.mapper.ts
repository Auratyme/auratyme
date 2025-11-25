import { ProfileResponseDto } from './dtos';
import { Profile } from './entities';
import { DbProfile } from './types/db.type';

export class ProfilesMapper {
  static dbToDomain(dbUser: DbProfile): Profile {
    return {
      ...dbUser,
      birthDate: dbUser.birthDate?.toISOString() || null,
    };
  }

  static domainToResponseDto(user: Profile): ProfileResponseDto {
    return user;
  }
}
