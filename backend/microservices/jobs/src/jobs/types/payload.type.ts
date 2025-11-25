export type JobPayload = Record<string, string> & {
  ackEventName: string;
};
