import { Module } from '@nestjs/common';
import { ClientsModule, Transport } from '@nestjs/microservices';

import { DiToken } from '@/src/common/enums';
import { BrokerService } from './broker.service';
import { loadConfig } from '@app/config';

@Module({
  imports: [
    ClientsModule.register([
      {
        name: DiToken.BROKER_CLIENT,
        transport: Transport.RMQ,
        options: {
          urls: [loadConfig().broker.amqpConnectionString],
          exchange: loadConfig().broker.exchangeName,
          exchangeType: 'topic',
          wildcards: true,
        },
      },
    ]),
  ],
  exports: [ClientsModule, BrokerService],
  providers: [BrokerService],
})
export class BrokerModule {}
