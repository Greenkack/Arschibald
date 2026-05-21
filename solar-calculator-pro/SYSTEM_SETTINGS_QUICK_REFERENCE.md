# System Settings - Quick Reference

## Overview

The System Settings module provides comprehensive system configuration and monitoring capabilities for Solar Calculator Pro. It includes general settings, email configuration, backup management, logging configuration, and system information display.

## Features

### 1. General Settings
- **Application Information**: Configure app name and description
- **Localization**: Set default language, currency, timezone, date/time formats
- **User Interface**: Configure items per page, session timeout
- **Features**: Enable/disable analytics, telemetry, maintenance mode

### 2. Email Configuration
- **Multiple Providers**: Support for SMTP, SendGrid, Mailgun, AWS SES
- **SMTP Settings**: Host, port, username, password, TLS/SSL
- **Email Settings**: From email, from name, reply-to email
- **Test Functionality**: Send test emails to verify configuration

### 3. Backup Settings
- **Automatic Backups**: Schedule backups (hourly, daily, weekly, monthly)
- **Backup Content**: Choose what to backup (database, files, logs)
- **Backup Options**: Compression, encryption, retention policy
- **Manual Backups**: Create backups on-demand
- **Backup History**: View and manage existing backups

### 4. Logging Configuration
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Destinations**: File, console, or both
- **Log Rotation**: Automatic rotation based on size and age
- **Log Content**: Configure what to log (API requests, database queries, errors)
- **Debug Mode**: Enable verbose logging for troubleshooting
- **Log Files**: View and manage log files

### 5. System Information
- **Overview**: Application version, system info, database info, performance metrics
- **Resources**: Real-time CPU, memory, and disk usage monitoring
- **Health Checks**: System health status for database, filesystem, memory, disk
- **Statistics**: User counts, project counts, calculations, PDFs, API calls, errors

## API Endpoints

### General Settings
- `GET /api/v1/system-settings/general` - Get general settings
- `PUT /api/v1/system-settings/general` - Update general settings

### Email Configuration
- `GET /api/v1/system-settings/email` - Get email settings
- `PUT /api/v1/system-settings/email` - Update email settings
- `POST /api/v1/system-settings/email/test` - Test email configuration

### Backup Settings
- `GET /api/v1/system-settings/backup` - Get backup settings
- `PUT /api/v1/system-settings/backup` - Update backup settings
- `POST /api/v1/system-settings/backup/create` - Create backup now
- `GET /api/v1/system-settings/backup/list` - List all backups

### Logging Configuration
- `GET /api/v1/system-settings/logging` - Get logging settings
- `PUT /api/v1/system-settings/logging` - Update logging settings
- `GET /api/v1/system-settings/logging/files` - List log files

### System Information
- `GET /api/v1/system-settings/info` - Get system information
- `GET /api/v1/system-settings/health` - Get system health status
- `GET /api/v1/system-settings/stats` - Get system statistics
- `GET /api/v1/system-settings/all` - Get all settings and info

## Usage

### Accessing System Settings

1. Navigate to **Admin Panel** in the application
2. Click on the **System Settings** tab
3. Use the sub-tabs to access different settings categories

### Configuring Email

1. Go to **Admin Panel > System Settings > Email**
2. Select your email provider (SMTP, SendGrid, etc.)
3. Enter the required credentials
4. Click **Test Email** to verify configuration
5. Click **Save Changes** to apply settings

### Creating Backups

1. Go to **Admin Panel > System Settings > Backup**
2. Configure automatic backup settings (frequency, retention)
3. Or click **Create Backup Now** for manual backup
4. Select what to include (database, files, logs)
5. Click **View Backups** to see backup history

### Monitoring System Health

1. Go to **Admin Panel > System Settings > System Info**
2. View **Overview** for general system information
3. Check **Resources** for CPU, memory, and disk usage
4. Review **Health** for component health status
5. See **Statistics** for usage metrics

## Configuration Files

### Settings Storage
- Location: `config/system_settings.json`
- Format: JSON
- Contains: All system settings (general, email, backup, logging)

### Backup Location
- Default: `backups/`
- Configurable in backup settings
- Backups can be compressed (ZIP) and encrypted

### Log Files
- Default: `logs/app.log`
- Configurable in logging settings
- Automatic rotation based on size and age

## Security Considerations

### Sensitive Data
- Passwords and API keys are not exposed in GET requests
- Encryption keys are stored securely
- Email passwords are only updated when provided

### Access Control
- System settings require administrator privileges
- All API endpoints should be protected with authentication
- Sensitive operations are logged

### Backup Security
- Backups can be encrypted with AES encryption
- Backup location should be secured
- Regular backup testing is recommended

## Best Practices

### General Settings
- Set appropriate session timeout for security
- Use maintenance mode during updates
- Configure timezone to match your location

### Email Configuration
- Always test email configuration after changes
- Use TLS/SSL for secure email transmission
- Keep SMTP credentials secure

### Backup Settings
- Enable automatic backups
- Set appropriate retention period (30 days recommended)
- Include database and files in backups
- Test backup restoration regularly
- Store backups in a secure location

### Logging Configuration
- Use INFO level for production
- Enable DEBUG mode only for troubleshooting
- Configure log rotation to prevent disk space issues
- Monitor log file sizes regularly
- Review error logs periodically

### System Monitoring
- Check system health regularly
- Monitor resource usage (CPU, memory, disk)
- Set up alerts for critical issues
- Review statistics for usage patterns

## Troubleshooting

### Email Not Sending
1. Verify SMTP host and port are correct
2. Check username and password
3. Ensure TLS/SSL settings match server requirements
4. Test with a known working email address
5. Check firewall settings

### Backup Failures
1. Verify backup location is writable
2. Check available disk space
3. Review backup logs for errors
4. Ensure database is accessible
5. Check file permissions

### High Resource Usage
1. Check for runaway processes
2. Review recent changes or updates
3. Analyze log files for errors
4. Consider increasing resources
5. Optimize database queries

### Log Files Growing Too Large
1. Enable log rotation
2. Reduce log level (INFO instead of DEBUG)
3. Decrease retention period
4. Disable verbose logging options
5. Archive old logs

## Support

For additional help:
- Check the full documentation in `/docs`
- Review API documentation at `/docs` (Swagger UI)
- Contact system administrator
- Check application logs for detailed error messages

## Version History

- **v1.0.0** (2024-01-01): Initial release
  - General settings management
  - Email configuration
  - Backup management
  - Logging configuration
  - System information display
