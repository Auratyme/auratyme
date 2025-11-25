import {
  ArgumentMetadata,
  Injectable,
  Logger,
  PipeTransform,
} from '@nestjs/common';
import { ZodError, ZodType } from 'zod';
import { GrpcInvalidArgumentException } from '../../exceptions/index.js';

@Injectable()
export class RpcValidationPipe implements PipeTransform {
  private logger = new Logger(RpcValidationPipe.name);

  constructor(private readonly schema: ZodType) {}

  transform(value: unknown, metadata: ArgumentMetadata) {
    try {
      const parsedValue = this.schema.parse(value);

      this.logger.debug('parsed request body: ', parsedValue);

      return parsedValue;
    } catch (err) {
      if (err instanceof ZodError) {
        throw new GrpcInvalidArgumentException('Validation failed', {
          errors: [
            ...err.issues.map((issue) => {
              return {
                fields: issue.path.length > 0 ? issue.path : null,
                code: issue.code,
                message: issue.message,
              };
            }),
          ],
        });
      }

      throw new GrpcInvalidArgumentException('Validation failed', null);
    }
  }
}
