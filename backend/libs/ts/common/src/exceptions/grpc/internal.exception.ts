import { GrpcException } from './grpc.exception.js';
import { status as GrpcStatus } from '@grpc/grpc-js';

export class GrpcInternalException extends GrpcException {
  constructor(message: string, details: unknown, cause?: unknown) {
    super(GrpcStatus.INTERNAL, message, details, cause);
  }
}
