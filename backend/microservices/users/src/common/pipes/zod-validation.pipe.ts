import {
  ArgumentMetadata,
  BadRequestException,
  Injectable,
  PipeTransform,
} from '@nestjs/common';
import { ZodError, ZodType } from 'zod';

@Injectable()
export class ZodValidationPipe implements PipeTransform {
  constructor(private readonly schema: ZodType) {}

  transform(value: unknown, metadata: ArgumentMetadata) {
    try {
      const parsedValue = this.schema.parse(value);
      return parsedValue;
    } catch (err) {
      if (err instanceof ZodError) {
        throw new BadRequestException(
          {
            message: 'Validation failed',
            errors: [
              ...err.issues.map((issue) => {
                return {
                  fields: issue.path.length > 0 ? issue.path : null,
                  code: issue.code,
                  message: issue.message,
                };
              }),
            ],
          },
          {},
        );
      }

      throw new BadRequestException('Validation failed');
    }
  }
}
