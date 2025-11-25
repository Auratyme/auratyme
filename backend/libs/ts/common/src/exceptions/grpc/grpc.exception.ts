import { RpcException } from '@nestjs/microservices';
import { ServiceError } from '@grpc/grpc-js';

export class GrpcException extends RpcException {
  constructor(
    statusCode: number,
    message: string,
    details: unknown,
    cause?: unknown
  ) {
    super({
      code: statusCode,
      message: message,
      details: details,
      cause: cause,
    } as ServiceError);
  }
}
