import { UpdateOptions } from 'common';
import { UsersUpdateFields } from '../helpers';

export type UserUpdateOptions = UpdateOptions<
  {
    id: string;
  },
  UsersUpdateFields
>;
