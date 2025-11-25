export function loadConfig() {
  return {
    app: {
      port: parseInt(process.env.PORT || '3000'),
    },
    db: {
      name: process.env.DB_NAME || 'notifications',
      port: parseInt(process.env.DB_PORT || '5432'),
      host: process.env.DB_HOST || 'notifications-db',
      user: process.env.DB_USER || 'admin',
      password: process.env.DB_PASSWORD || '',
      passwordFile: process.env.DB_PASSWORD_FILE || '',
    },
    auth: {
      publicKeyPath: process.env.PUBLIC_KEY_PATH!,
    },
    broker: {
      amqpConnectionString: process.env.AMQP_CONNECTION_STRING!,
      queueName: process.env.QUEUE_NAME!,
      exchangeName: process.env.EXCHANGE_NAME!,
    },
  };
}
