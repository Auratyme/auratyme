import { Injectable, Logger } from '@nestjs/common';
import {
  ExpoPushMessage,
  Expo,
  ExpoPushTicket,
  ExpoPushReceiptId,
} from 'expo-server-sdk';
import { PushTokenService } from '../push-token/push-token.service';
import { PushNotification } from './types';
import { PushNotificationException } from './exceptions';

@Injectable()
export class PushNotificationService {
  private readonly logger = new Logger(PushNotificationService.name);
  private readonly expo = new Expo();

  constructor(private readonly pushTokenService: PushTokenService) {}

  async sendPushNotifications(
    message: PushNotification,
    userId: string,
  ): Promise<void> {
    this.logger.log('Sending push notifications...');

    const pushTokens = (await this.pushTokenService.find(userId)).map(
      (val) => val.pushToken,
    );

    let messages: ExpoPushMessage[] = [];

    for (let pushToken of pushTokens) {
      if (!Expo.isExpoPushToken(pushToken)) {
        this.logger.error(`${pushToken} is not a valid push token`);
        continue;
      }

      messages.push({
        ...message,
        to: pushToken,
      });
    }

    let chunks = this.expo.chunkPushNotifications(messages);

    let tickets: ExpoPushTicket[] = [];

    for (let chunk of chunks) {
      let ticketChunk = await this.expo.sendPushNotificationsAsync(chunk);
      this.logger.debug(JSON.stringify(ticketChunk));
      tickets.push(...ticketChunk);
    }

    let receiptIds: ExpoPushReceiptId[] = [];

    for (let ticket of tickets) {
      if (ticket.status === 'ok') {
        receiptIds.push(ticket.id);
      }
    }

    let receiptIdChunks = this.expo.chunkPushNotificationReceiptIds(receiptIds);

    for (let chunk of receiptIdChunks) {
      let receipts = await this.expo.getPushNotificationReceiptsAsync(chunk);
      console.log(receipts);

      for (let receiptId in receipts) {
        let { status, details } = receipts[receiptId];

        if (status === 'ok') {
          continue;
        } else if (status === 'error') {
          let cause;

          if (details) {
            cause = details;
          }

          this.logger.error(
            'There was an error sending a notification, cause: ',
            cause,
          );
        }
      }
    }
  }
}
