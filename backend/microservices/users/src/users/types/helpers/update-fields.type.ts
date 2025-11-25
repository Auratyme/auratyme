import { DbUser } from '../db.type';

export type UsersUpdateFields = Omit<
  Partial<DbUser>,
  'id' | 'createdAt' | 'updatedAt'
>;
