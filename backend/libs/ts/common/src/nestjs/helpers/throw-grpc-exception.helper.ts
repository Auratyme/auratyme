import { status as GrpcStatus } from '@grpc/grpc-js';
import { throwError } from 'rxjs';
import {
  GrpcFailedPreconditionException,
  GrpcInternalException,
  GrpcNotFoundException,
} from '../../exceptions/index.js';
import { RpcException } from '@nestjs/microservices';

export function throwGrpcException(statusCode: GrpcStatus, err: RpcException) {
  switch (statusCode) {
    case GrpcStatus.INVALID_ARGUMENT:
      return throwError(
        () => new GrpcInternalException(err?.message || '', null, err)
      );
    case GrpcStatus.NOT_FOUND:
      return throwError(
        () => new GrpcNotFoundException(err?.message || '', null, err)
      );
    case GrpcStatus.FAILED_PRECONDITION:
      return throwError(
        () => new GrpcFailedPreconditionException(err?.message || '', null, err)
      );
    case GrpcStatus.INTERNAL:
      return throwError(
        () => new GrpcInternalException(err?.message || '', null, err)
      );
    default:
      return throwError(
        () => new GrpcInternalException(err?.message || '', null, err)
      );
  }
}
