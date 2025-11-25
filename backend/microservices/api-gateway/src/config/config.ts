export function loadConfig() {
  return {
    app: {
      nodeEnv: process.env.NODE_ENV || 'production',
      port: parseInt(process.env.PORT || '3000'),
      schedulesServiceHost: process.env.SCHEDULES_SERVICE_HOST || '',
      notificationsServiceHost: process.env.NOTIFICATIONS_SERVICE_HOST || '',
      usersServiceHost: process.env.USERS_SERVICE_HOST || '',
    },
    auth: {
      oauthTenantDomain: process.env.OAUTH_TENANT_DOMAIN!,
      auratymeApiId: process.env.AURATYME_API_ID!,
      publicKeyPath: process.env.PUBLIC_KEY_PATH!,
    },
  } as const;
}
