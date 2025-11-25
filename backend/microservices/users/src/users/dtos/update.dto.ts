import { UsersUpdateFields } from '../types/helpers';

export class UserUpdateDto {
  where: {
    id: string;
  };
  fields?: UsersUpdateFields;
}
