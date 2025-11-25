import {
  CallHandler,
  ExecutionContext,
  Injectable,
  Logger,
  NestInterceptor,
} from '@nestjs/common';
import { catchError, Observable, tap } from 'rxjs';

@Injectable()
export class RpcRequestInterceptor implements NestInterceptor {
  private readonly logger = new Logger(RpcRequestInterceptor.name);

  intercept(
    context: ExecutionContext,
    next: CallHandler<unknown>
  ): Observable<unknown> {
    const now = Date.now();

    this.logger.log(
      `incoming rpc request: ${context.getClass().name}.${context.getHandler().name}`
    );
    this.logger.debug('request payload: ', context.switchToRpc().getData());

    return next.handle().pipe(
      tap(() => {
        this.logger.log(
          `response to ${context.getClass().name}.${context.getHandler().name}, latency ${Date.now() - now}ms`
        );
      })
    );
  }
}
