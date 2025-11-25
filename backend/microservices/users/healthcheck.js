fetch('http://localhost:3000/healthcheck')
  .then((res) => {
    if (res.status >= 500) {
      throw new Error('Service unhealthy');
    }
  })
  .catch((err) => {
    throw new Error('Service unhealthy', {
      cause: err,
    });
  });
