import { Inject, Injectable, Logger } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';

import { DiToken } from '@/src/common/enums';

@Injectable()
export class BrokerService {
  private readonly logger = new Logger(BrokerService.name);

  constructor(
    @Inject(DiToken.BROKER_CLIENT)
    private readonly brokerClient: ClientProxy,
  ) {}

  publishEvent<EventPayload = unknown>(
    eventPattern: string,
    payload: EventPayload,
  ) {
    try {
      this.brokerClient.emit(eventPattern, payload);
    } catch (err) {
      this.logger.error(err);
    }
  }

  publishTask<TaskPayload = unknown>(
    taskPattern: string,
    payload: TaskPayload,
  ) {
    try {
      this.brokerClient.emit(taskPattern, payload);
    } catch (err) {
      this.logger.error(err);
    }
  }

  connect() {
    return this.brokerClient.connect();
  }

  close() {
    this.brokerClient.close();
  }
}
