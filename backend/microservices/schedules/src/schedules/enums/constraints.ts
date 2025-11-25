export const SchedulesConstraints = {
  MAX_DESCRIPTION_LENGTH: 500,
  MAX_NAME_LENGTH: 200,
  MAX_USER_ID_LENGTH: 255,

  MIN_LIMIT: 10,
  MAX_LIMIT: 100,
  DEFAULT_LIMIT: 50,

  MIN_PAGE: 0,
  DEFAULT_PAGE: 0,

  DEFAULT_ORDER_BY: 'createdAt',

  DEFAULT_SORT_BY: 'desc',
} as const;
