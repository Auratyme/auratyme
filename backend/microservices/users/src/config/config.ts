export function loadConfig() {
  return {
    app: {
      nodeEnv: process.env.NODE_ENV || 'production',
      port: parseInt(process.env.PORT || '3000'),
    },
    db: {
      name: process.env.DB_NAME || 'schedules',
      port: parseInt(process.env.DB_PORT || '5432'),
      host: process.env.DB_HOST || 'schedules-db',
      user: process.env.DB_USER || 'admin',
      password: process.env.DB_PASSWORD || '',
      passwordFile: process.env.DB_PASSWORD_FILE || '',
    },
    auth: {
      oauthTenantDomain: process.env.OAUTH_TENANT_DOMAIN!,
      auratymeApiId: process.env.AURATYME_API_ID!,
      publicKeyPath: process.env.PUBLIC_KEY_PATH!,
    },
  } as const;
}
