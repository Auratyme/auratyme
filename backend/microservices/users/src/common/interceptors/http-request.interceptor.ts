import {
  CallHandler,
  ExecutionContext,
  Injectable,
  Logger,
  NestInterceptor,
} from '@nestjs/common';
import { Observable, tap } from 'rxjs';
import { Request, Response } from 'express';

@Injectable()
export class HttpRequestInterceptor implements NestInterceptor {
  private readonly logger = new Logger(HttpRequestInterceptor.name);

  intercept(
    context: ExecutionContext,
    next: CallHandler<unknown>,
  ): Observable<unknown> | Promise<Observable<unknown>> {
    const http = context.switchToHttp();
    const req = http.getRequest<Request>();
    const res = http.getResponse<Response>();
    const now = Date.now();

    if (req.path === '/healthcheck') {
      return next.handle();
    }

    this.logger.log(`incoming request: [HTTP ${req.method}] ${req.path}`);

    return next.handle().pipe(
      tap(() => {
        this.logger.log(
          `response: [HTTP ${req.method}] ${res.statusCode} ${req.path} (latency: ${Date.now() - now}ms)`,
        );
      }),
    );
  }
}
