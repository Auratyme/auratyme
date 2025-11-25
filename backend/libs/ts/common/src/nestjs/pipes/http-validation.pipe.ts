import {
  ArgumentMetadata,
  BadRequestException,
  HttpStatus,
  Injectable,
  Logger,
  PipeTransform,
} from '@nestjs/common';
import { ZodError, ZodType } from 'zod';
import { ApiException } from '../../exceptions/api.exception.js';

@Injectable()
export class ZodValidationPipe implements PipeTransform {
  private logger = new Logger(ZodValidationPipe.name);

  constructor(private readonly schema: ZodType) {}

  transform(value: unknown, metadata: ArgumentMetadata) {
    try {
      const parsedValue = this.schema.parse(value);

      this.logger.debug('parsed request: ', parsedValue);

      return parsedValue;
    } catch (err) {
      if (err instanceof ZodError) {
        const validationErrors = [
          ...err.issues.map((issue) => {
            return {
              fields: issue.path.length > 0 ? issue.path : null,
              code: issue.code,
              message: issue.message,
            };
          }),
        ];

        throw new BadRequestException(
          new ApiException(HttpStatus.BAD_REQUEST, 'validation failed', null, {
            errors: validationErrors,
          })
        );
      }

      throw new BadRequestException(
        new ApiException(
          HttpStatus.BAD_REQUEST,
          'validation failed',
          null,
          null
        )
      );
    }
  }
}
