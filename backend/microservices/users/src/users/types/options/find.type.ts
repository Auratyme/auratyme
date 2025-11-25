import { FindOptions } from 'common';
import { DbUser } from '../db.type';

export type UsersFindOptions = FindOptions<never, Exclude<keyof DbUser, 'id'>>;
