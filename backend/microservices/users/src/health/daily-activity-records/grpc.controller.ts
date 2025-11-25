import { Controller, Logger } from '@nestjs/common';
import { DailyActivityRecordsService } from './daily-activity-records.service';
import { GrpcMethod } from '@nestjs/microservices';
import { Metadata, ServerUnaryCall } from '@grpc/grpc-js';

@Controller()
export class GrpcDailyActivityRecordsController {
  private readonly logger = new Logger(GrpcDailyActivityRecordsController.name);

  constructor(
    private readonly dailyActivityRecordsService: DailyActivityRecordsService,
  ) {}

  @GrpcMethod('DailyActivityRecordsService', 'Test')
  test(
    data: { id: string },
    metadata: Metadata,
    call: ServerUnaryCall<unknown, unknown>,
  ) {
    this.logger.debug('DailyActivityRecordsService Test called');

    return { id: 'test' };
  }
}
