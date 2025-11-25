import { JwtPayload } from 'jsonwebtoken';

declare global {
  namespace Express {
    interface Request {
      auth: {
        user: {
          id: string;
        };
      };
    }
  }
}

