import { FindOneOptions } from 'common';

export type UserFindOneOptions = FindOneOptions<{
  id: string;
}>;
