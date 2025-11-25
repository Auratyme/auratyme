import { UsersOrderByFields } from '../types/helpers';

export class UsersFindDto {
  options?: {
    limit?: number;
    page?: number;
    orderBy?: UsersOrderByFields;
    sortBy?: 'asc' | 'desc';
  };
}
