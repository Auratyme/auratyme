export class JobScheduleSingleDto {
  name: string;
  executionDate: string;
  ackEventName: string;
  payload: Record<string, string>;
}
