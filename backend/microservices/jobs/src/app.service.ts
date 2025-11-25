import {
  Injectable,
  OnApplicationBootstrap,
  OnApplicationShutdown,
} from '@nestjs/common';

import { BrokerService } from './broker/broker.service';

@Injectable()
export class AppService
  implements OnApplicationBootstrap, OnApplicationShutdown {
  constructor(private readonly brokerService: BrokerService) { }

  async onApplicationBootstrap() {
    await this.brokerService.connect();
  }

  onApplicationShutdown() {
    this.brokerService.close();
  }
}
