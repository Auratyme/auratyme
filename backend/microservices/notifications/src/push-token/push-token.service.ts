import { Injectable } from '@nestjs/common';
import { PushTokenRepository } from './push-token.repository';

@Injectable()
export class PushTokenService {
  constructor(private readonly pushTokenRepository: PushTokenRepository) {}

  async save(pushToken: string, userId: string): Promise<void> {
    return this.pushTokenRepository.save(pushToken, userId);
  }

  async find(userId: string): Promise<{ pushToken: string }[]> {
    return this.pushTokenRepository.find(userId);
  }

  async remove(pushToken: string, userId: string): Promise<void> {
    return this.pushTokenRepository.remove(pushToken, userId);
  }
}
