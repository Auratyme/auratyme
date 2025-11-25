import { Task } from '../entities';
import {
  OmitType,
  PickType,
  IntersectionType,
  PartialType,
} from '@nestjs/mapped-types';

const OptionalFields = PartialType(
  OmitType(Task, ['id', 'createdAt', 'updatedAt'] as const),
);
const RequiredFields = PickType(Task, [
  'name',
  'scheduleId',
  'userId',
] as const);

export class TaskCreateDto extends IntersectionType(
  OptionalFields,
  RequiredFields,
) {}
