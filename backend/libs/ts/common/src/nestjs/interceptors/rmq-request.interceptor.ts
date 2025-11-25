import {
  CallHandler,
  ExecutionContext,
  Injectable,
  Logger,
  NestInterceptor,
} from '@nestjs/common';
import { RmqContext } from '@nestjs/microservices';
import { Observable, tap } from 'rxjs';

@Injectable()
export class RmqRequestInterceptor implements NestInterceptor {
  private logger = new Logger(RmqRequestInterceptor.name);

  intercept(
    context: ExecutionContext,
    next: CallHandler<unknown>,
  ): Observable<unknown> | Promise<Observable<unknown>> {
    const rpc = context.switchToRpc();
    const rmqContext = rpc.getContext<RmqContext>();
    const pattern = rmqContext.getPattern();
    const startTime = Date.now();
    const handlerName = context.getHandler().name;

    this.logger.log(
      `incoming rmq message: ${pattern}, handler: ${handlerName} `,
    );

    return next.handle().pipe(
      tap(() => {
        const latency = Date.now() - startTime;
        this.logger.log(
          `rmq message ${pattern} handled by ${handlerName} with latency: ${latency}ms`,
        );
      }),
    );
  }
}
