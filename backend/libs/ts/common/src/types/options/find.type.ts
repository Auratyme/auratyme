export type FindOptions<
  Where extends Record<string, unknown>,
  OrderBy extends string = string,
> = {
  limit?: number;
  page?: number;
  orderBy?: OrderBy;
  sortBy?: 'asc' | 'desc';
  where?: Where;
};
