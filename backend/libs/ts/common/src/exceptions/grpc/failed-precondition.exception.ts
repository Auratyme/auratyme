import { GrpcException } from './grpc.exception.js';
import { status as GrpcStatus } from '@grpc/grpc-js';

export class GrpcFailedPreconditionException extends GrpcException {
  constructor(message: string, details: unknown, cause?: unknown) {
    super(GrpcStatus.FAILED_PRECONDITION, message, details, cause);
  }
}
