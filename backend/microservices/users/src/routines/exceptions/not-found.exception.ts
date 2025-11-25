import { RoutineException } from './routine.exception';

export class RoutineNotFoundException extends RoutineException {
  constructor(id: string) {
    super(`Routine with id = ${id} was not found`);
  }
}
