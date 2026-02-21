# Eclipse Ditto Configuration

This directory contains custom configuration for Eclipse Ditto services.

## Default Configuration

Eclipse Ditto uses default configuration values that work well for most deployments.
The docker-compose.yml file sets environment variables to override defaults where needed.

## Environment Variables

Key environment variables used:

### MongoDB Connection
- `MONGO_DB_URI`: MongoDB connection string
- `MONGO_DB_CONNECTION_POOL_SIZE`: Connection pool size (default: 20)
- `MONGO_DB_READ_PREFERENCE`: Read preference (primaryPreferred, secondaryPreferred, etc.)

### JVM Options
- `JAVA_TOOL_OPTIONS`: JVM options including memory limits

### Gateway Authentication
- `ENABLE_PRE_AUTHENTICATION`: Enable pre-authenticated requests
- DevOps password is set via JAVA_TOOL_OPTIONS

## Custom Configuration Files

If you need to customize Ditto beyond environment variables, you can mount configuration files:

1. Create a config file for the specific service (e.g., `gateway.conf`)
2. Mount it in docker-compose.yml to `/opt/ditto/application.conf`
3. Restart the service

Example docker-compose override:
```yaml
gateway:
  volumes:
    - ./ditto/gateway.conf:/opt/ditto/application.conf:ro
```

## References

- [Ditto Configuration Documentation](https://eclipse.dev/ditto/installation-operating.html)
- [Gateway Configuration](https://github.com/eclipse-ditto/ditto/blob/master/gateway/service/src/main/resources/gateway.conf)
- [Things Configuration](https://github.com/eclipse-ditto/ditto/blob/master/things/service/src/main/resources/things.conf)
