# Email Tracker

Flask-based email tracking application that monitors your inbox and provides a web interface for viewing emails and attachments. The application features real-time email monitoring with WebSocket support and attachment handling for both web UI and REST API endpoints.

## Features

### Core Functionality
- **Real-time Email Monitoring** - Automatically tracks new emails using IMAP with live WebSocket updates
- **Modern Web Interface** - Responsive dashboard built with Tailwind CSS and real-time notifications
- **Attachment Support** - Download and preview attachments (images, PDFs, text files) with inline viewer
- **Database Storage** - SQLite database for persistent email storage with duplicate prevention
- **Live Statistics** - Real-time dashboard updates showing email counts and monitoring status
- **Timezone Support** - Configurable timezone (default: GMT+3)

### Web Interface
- **Dashboard** - Live overview with email statistics and recent emails
- **Email List** - Searchable and filterable email listing with real-time additions
- **Email Details** - Full email content view with attachment management and preview
- **Attachment Viewer** - In-browser preview for images, PDFs, and text files
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices

### API Endpoints
- **REST API** - Complete programmatic access to email data
- **Health Monitoring** - Application health check endpoint
- **File Downloads** - Direct attachment download and viewing capabilities
- **Statistics API** - Live statistics endpoint for external integrations

## Requirements

- Python 3.8+
- Gmail account with App Password (or other IMAP-enabled email provider)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/email-tracker.git
cd email-tracker
```

### 2. Create Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:

```env
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your-app-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SECRET_KEY=your-secret-key-here
```

**Important**: For Gmail, use an App Password instead of your regular password:
1. Enable 2-Step Verification in Google Account settings
2. Go to Security > 2-Step Verification > App passwords
3. Generate a new app password for "Mail"
4. Use this password in the `.env` file

**Generate Secret Key**: Run `python -c "import secrets; print(secrets.token_hex(32))"` to generate a secure secret key.

### 5. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000` with real-time WebSocket support enabled.

## Usage

### Web Interface

1. **Dashboard** (`/`) - Real-time view of email statistics and recent emails with live updates
2. **Email List** (`/emails`) - Browse all emails with search, filter, and real-time new email notifications
3. **Email Details** (`/emails/<id>`) - View full email content with attachment preview and download

### API Endpoints

#### Web Routes
- `GET /` - Dashboard page with live statistics
- `GET /emails` - Email list page with real-time updates
- `GET /emails/<id>` - Email detail page with attachment viewer
- `GET /stats` - Live statistics endpoint (JSON)

#### API Routes
- `GET /api/emails` - List all emails (JSON)
- `GET /api/emails/<id>/attachments` - List email attachments (JSON)
- `GET /api/attachments/<id>/download` - Download attachment
- `GET /api/attachments/<id>/view` - View attachment inline
- `GET /api/health` - Health check endpoint

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

- Email composition and sending capabilities
- Advanced search with date ranges and content filtering
- Email labeling and categorization system
- Export functionality (CSV, PDF, MBOX formats)
- Multiple email account support with account switching
- Email templates and automation rules
- Advanced attachment preview (Office documents, videos)
- Email statistics and analytics dashboard
- User authentication and multi-user support
- Email archiving and automated cleanup tools
- Mobile application with push notifications
- Integration with external services (Slack, Discord)
- Advanced real-time features (typing indicators, presence)
- Email threading and conversation grouping

---

**Note**: This application is designed for personal use and development purposes. Ensure you comply with your email provider's terms of service and applicable privacy regulations when using this software. The real-time features require a modern web browser with WebSocket support for optimal functionality.