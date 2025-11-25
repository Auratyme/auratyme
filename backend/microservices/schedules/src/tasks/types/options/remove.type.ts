import { RemoveOptions } from 'common';

export type TaskRemoveOptions = RemoveOptions<{
  id: string;
  userId?: string;
}>;
