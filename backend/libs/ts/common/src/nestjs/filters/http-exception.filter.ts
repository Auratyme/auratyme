import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  Logger,
} from '@nestjs/common';

import { Request, Response } from 'express';
import { ApiException } from '../../exceptions/api.exception.js';

@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpException.name);

  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();
    const status = exception.getStatus();

    const message = `[HTTP ${request.method}] ${exception.getStatus()} ${request.path} - ${exception.message}`;
    const exceptionResponse = exception.getResponse();
    const errorResponse =
      typeof exceptionResponse === 'string'
        ? { message: exceptionResponse }
        : exceptionResponse;

    if (status >= 400 && status < 500) {
      this.logger.warn(message);
    } else {
      this.logger.error(message);
      this.logger.debug(exception.cause);
    }

    response
      .status(status)
      .json(
        new ApiException(
          status,
          (errorResponse as any).message,
          (errorResponse as any).code || null,
          (errorResponse as any).details || null
        )
      );
  }
}
