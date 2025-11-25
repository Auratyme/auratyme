export class ApiException {
  private timestamp: string;

  constructor(
    private readonly statusCode: number,
    private readonly message: string,
    private readonly code?: string,
    private readonly details?: Record<string, unknown>,
  ) {
    this.timestamp = new Date().toISOString();
  }
}
