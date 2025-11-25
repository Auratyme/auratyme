import {
  ArgumentsHost,
  Catch,
  Logger,
  RpcExceptionFilter as NestRpcExceptionFilter,
} from '@nestjs/common';
import { RpcException } from '@nestjs/microservices';
import { Observable, throwError } from 'rxjs';
import { status as GrpcStatus, ServiceError } from '@grpc/grpc-js';

@Catch(RpcException)
export class RpcExceptionFilter
  implements NestRpcExceptionFilter<RpcException>
{
  private readonly logger = new Logger(RpcExceptionFilter.name);

  constructor() {}

  catch(exception: RpcException, host: ArgumentsHost): Observable<unknown> {
    const ctx = host.switchToRpc();
    const error = exception.getError();

    this.logger.error(exception);

    const grpcError =
      typeof error === 'object' && error != null
        ? error
        : ({
            code: GrpcStatus.UNKNOWN,
            message: exception.message,
            details: error.toString(),
          } as ServiceError);

    return throwError(() => grpcError);
  }
}
