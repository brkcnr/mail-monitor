# Email Tracker

Flask-based email tracking application that monitors your inbox and provides a web interface for viewing emails and attachments. The application features real-time email monitoring, attachment handling and both web UI and REST API endpoints.

## Features

### Core Functionality
- **Real-time Email Monitoring** - Automatically tracks new emails using IMAP
- **Web Interface** - Modern, responsive dashboard built with Tailwind CSS
- **Attachment Support** - Download and preview attachments (images, PDFs, text files)
- **Database Storage** - SQLite database for persistent email storage
- **Duplicate Prevention** - Intelligent handling of duplicate emails
- **Timezone Support** - Configurable timezone (default: GMT+3)

### Web Interface
- **Dashboard** - Overview with email statistics and recent emails
- **Email List** - Searchable and filterable email listing
- **Email Details** - Full email content view with attachment management
- **Attachment Viewer** - In-browser preview for supported file types
- **Responsive Design** - Works on desktop, tablet, and mobile devices

### API Endpoints
- **REST API** - Complete programmatic access to email data
- **Health Monitoring** - Application health check endpoint
- **File Downloads** - Direct attachment download capabilities

## Requirements

- Python 3.8+
- Gmail account with App Password (or other IMAP-enabled email)

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
```

**Important**: For Gmail, use an App Password instead of your regular password:
1. Enable 2-Step Verification in Google Account settings
2. Go to Security > 2-Step Verification > App passwords
3. Generate a new app password for "Mail"
4. Use this password in the `.env` file

### 5. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### Web Interface

1. **Dashboard** (`/`) - View email statistics and recent emails
2. **Email List** (`/emails`) - Browse all emails with search and filter options
3. **Email Details** (`/emails/<id>`) - View full email content and attachments

### API Endpoints

#### Web Routes
- `GET /` - Dashboard page
- `GET /emails` - Email list page
- `GET /emails/<id>` - Email detail page
- `GET /stats` - Live statistics (AJAX endpoint)

#### API Routes
- `GET /api/emails` - List all emails (JSON)
- `GET /api/emails/<id>/attachments` - List email attachments (JSON)
- `GET /api/attachments/<id>/download` - Download attachment
- `GET /api/attachments/<id>/view` - View attachment inline
- `GET /api/health` - Health check

## Configuration

### .env Settings
- `EMAIL_ADDRESS` - Your email address
- `EMAIL_PASSWORD` - Your email password or app password
- `IMAP_SERVER` - IMAP server (default: imap.gmail.com)
- `IMAP_PORT` - IMAP port (default: 993)

### Application Settings
- `CHECK_INTERVAL` - Email check frequency in seconds (default: 60)
- `MAX_RETRIES` - Maximum connection retry attempts (default: 3)
- `RETRY_DELAY` - Delay between retries in seconds (default: 60)
- `TIMEZONE` - Application timezone (default: GMT+3)
- `DEBUG` - Flask debug mode (default: True)
- `PORT` - Application port (default: 5000)

## Development

### Architecture
- **Flask Application Factory** - Modular app creation
- **Blueprint Organization** - Separate API and web routes
- **Service Layer** - Business logic separation
- **Data Models** - Type-safe data structures
- **Context Managers** - Proper resource handling

### Adding Features
1. **New Routes** - Add to appropriate blueprint in `app/routes/`
2. **Database Changes** - Modify `app/services/db.py`
3. **Frontend** - Update templates in `app/templates/`
4. **JavaScript** - Add functionality to `app/static/app.js`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Email composition and sending
- [ ] Advanced search with date ranges
- [ ] Email labeling and categorization
- [ ] Export functionality (CSV, PDF)
- [ ] Multiple email account support
- [ ] Email templates and automation
- [ ] Advanced attachment preview (Office docs)
- [ ] Email statistics and analytics
- [ ] User authentication and multi-user support
- [ ] Email archiving and cleanup tools

---

**Note**: This application is designed for personal use and development purposes. Ensure you comply with your email provider's terms of service and applicable privacy regulations when using this software.
