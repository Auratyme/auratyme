import { FindOptions } from 'common';
import { DbProfile } from '../db.type';

export type ProfilesFindOptions = FindOptions<
  Partial<DbProfile>,
  keyof DbProfile
>;
