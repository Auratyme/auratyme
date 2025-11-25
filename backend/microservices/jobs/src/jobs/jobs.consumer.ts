import { Processor, WorkerHost } from '@nestjs/bullmq';
import { Logger } from '@nestjs/common';
import { Job } from 'bullmq';

import { loadConfig } from '@app/config';
import { BrokerService } from '@app/broker/broker.service';

import { JobPayload } from './types';

@Processor(loadConfig().broker.jobsQueueName)
export class JobsConsumer extends WorkerHost {
  private readonly logger = new Logger(JobsConsumer.name);

  constructor(private readonly brokerService: BrokerService) {
    super();
  }

  async process(job: Job<JobPayload>): Promise<unknown> {
    this.logger.debug(`New job in a queue: ${job.name}, id: ${job.id}`);
    this.logger.debug(`Payload:`);
    this.logger.debug(job.data);

    this.brokerService.publishEvent(job.data.ackEventName, job.data);

    return Promise.resolve(null);
  }
}
