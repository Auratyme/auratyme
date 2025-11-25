export function loadConfig() {
  return {
    app: {
      nodeEnv: process.env.NODE_ENV || 'production',
      port: parseInt(process.env.PORT || '3000'),
    },
    db: {
      host: process.env.DB_HOST || 'jobs-db',
      port: parseInt(process.env.DB_PORT || '6379'),
    },
    broker: {
      amqpConnectionString:
        process.env.AMQP_CONNECTION_STRING || 'amqp://broker:5672',
      jobsQueueName: process.env.JOBS_QUEUE_NAME || 'jobs.queue',
      exchangeName: process.env.EXCHANGE_NAME || 'auratyme',
    },
    jobsClient: {
      url: process.env.JOB_SERVICE_URL,
    },
  };
}
