import { GrpcException } from './grpc.exception.js';
import { status as GrpcStatus } from '@grpc/grpc-js';

export class GrpcNotFoundException extends GrpcException {
  constructor(message: string, details: unknown, cause?: unknown) {
    super(GrpcStatus.NOT_FOUND, message, details, cause);
  }
}
