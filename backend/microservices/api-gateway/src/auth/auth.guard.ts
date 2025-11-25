import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
  Logger,
  BadRequestException,
  HttpStatus,
} from '@nestjs/common';
import { JwtService, JsonWebTokenError } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { Request } from 'express';

import { AuthConfig } from '@app/common/types';
import { readFile } from 'node:fs/promises';
import { JwtPayload } from 'jsonwebtoken';
import { ApiException } from 'common';

@Injectable()
export class AuthGuard implements CanActivate {
  private readonly config: AuthConfig;
  private readonly logger = new Logger(AuthGuard.name);

  constructor(
    private configService: ConfigService,
    private jwtService: JwtService,
  ) {
    this.config = this.configService.get<AuthConfig>('auth', {
      infer: true,
    }) as AuthConfig;
  }

  extractTokenFromHeader(req: Request): string | undefined {
    const token = req.headers['authorization']?.split(' ')[1];
    return token;
  }

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request>();
    const token = this.extractTokenFromHeader(request);

    if (token === undefined) {
      throw new UnauthorizedException(
        new ApiException(
          HttpStatus.UNAUTHORIZED,
          'No token in authorization header',
        ),
      );
    }

    const cert = await readFile(
      `${process.cwd()}/${this.config.publicKeyPath}`,
    );

    try {
      const payload: JwtPayload = await this.jwtService.verifyAsync(token, {
        issuer: this.config.oauthTenantDomain,
        audience: this.config.auratymeApiId,
        publicKey: cert,
      });

      const userId = payload.sub;

      if (!userId) {
        throw new BadRequestException(
          new ApiException(
            HttpStatus.BAD_REQUEST,
            'No sub field in JWT token present',
          ),
        );
      }

      request.auth = {
        user: {
          id: userId,
        },
      };

      return true;
    } catch (err) {
      let errorMessage = '';

      if (err instanceof JsonWebTokenError) {
        errorMessage += `${err.message}`;
      }

      throw new ForbiddenException(
        new ApiException(HttpStatus.FORBIDDEN, errorMessage),
        { cause: err },
      );
    }
  }
}
