import { Controller, Logger } from '@nestjs/common';
import { SleepRecordsService } from './sleep-records.service';
import { GrpcMethod } from '@nestjs/microservices';
import { Metadata, ServerUnaryCall } from '@grpc/grpc-js';

@Controller()
export class GrpcSleepRecordsController {
  private readonly logger = new Logger(GrpcSleepRecordsController.name);

  constructor(private readonly sleepRecordsService: SleepRecordsService) {}

  @GrpcMethod('SleepRecordsService', 'Test')
  test(
    data: { id: string },
    metadata: Metadata,
    call: ServerUnaryCall<unknown, unknown>,
  ) {
    this.logger.debug('SleepRecordsService Test called');

    return { id: 'test' };
  }
}
