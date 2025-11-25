export class ApiException {
  private timestamp: string;
  private code: string | null;
  private details: Record<string, unknown> | null;

  constructor(
    public readonly statusCode: number,
    public readonly message: string,
    code?: string | null,
    details?: Record<string, unknown> | null
  ) {
    this.timestamp = new Date().toISOString();
    this.code = code || null;
    this.details = details || null;
  }
}
