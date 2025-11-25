import {
  Body,
  Controller,
  HttpCode,
  HttpStatus,
  InternalServerErrorException,
  Post,
  UseGuards,
} from '@nestjs/common';
import { Request } from 'express';
import { z } from 'zod';

import { AuthGuard } from '@/src/auth/auth.guard';
import { ZodValidationPipe } from '@/src/common/pipes';
import { uploadPushTokenSchema } from './schemas';
import { User } from '@/src/common/decorators';
import { PushTokenService } from './push-token.service';

@UseGuards(AuthGuard)
@Controller({
  path: '/push-tokens',
})
export class PushTokenController {
  constructor(private readonly pushTokenService: PushTokenService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async upload(
    @Body(new ZodValidationPipe(uploadPushTokenSchema))
    body: z.infer<typeof uploadPushTokenSchema>,
    @User() user: Request['auth']['user'],
  ) {
    try {
      await this.pushTokenService.save(body.pushToken, user.id);
    } catch (err) {
      throw new InternalServerErrorException(
        { message: 'Failed to save push token' },
        { cause: err },
      );
    }
  }
}
