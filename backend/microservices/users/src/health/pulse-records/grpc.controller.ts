import { Controller, Logger } from '@nestjs/common';
import { PulseRecordsService } from './pulse-records.service';
import { GrpcMethod } from '@nestjs/microservices';
import { Metadata, ServerUnaryCall } from '@grpc/grpc-js';

@Controller()
export class GrpcPulseRecordsController {
  private readonly logger = new Logger(GrpcPulseRecordsController.name);

  constructor(private readonly pulseRecordsService: PulseRecordsService) {}

  @GrpcMethod('PulseRecordsService', 'Test')
  test(
    data: { id: string },
    metadata: Metadata,
    call: ServerUnaryCall<unknown, unknown>,
  ) {
    this.logger.debug('PulseRecordsService Test called');

    return { id: 'test' };
  }
}
