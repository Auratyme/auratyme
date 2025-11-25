export class JobScheduleCronDto {
  name: string;
  cron: string;
  ackEventName: string;
  payload: Record<string, string>;
}
