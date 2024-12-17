# Email Tracker

A Flask-based email tracking application that monitors your inbox and stores email details in a SQLite database.

## Features

- Real-time email monitoring using IMAP
- Stores email metadata (sender, subject, body, received date)
- Handles email attachments
- Prevents duplicate email entries
- REST API endpoints for email data access
- Timezone support (GMT+3)

## Setup

1. Clone the repository:
```bash
git clone <https://github.com/brkcnr/mail-monitor.git>
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your email credentials:
```env
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your-app-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
```

Note: For Gmail, use an App Password instead of your regular password. You can generate one in your Google Account settings under Security > 2-Step Verification > App passwords.

## Usage

1. Start the application:
```bash
python app.py
```

2. The application will:
- Initialize the SQLite database (if not exists)
- Start monitoring your inbox for new emails
- Mark processed emails as seen
- Store email details in the database

3. Access email data through the following endpoints:
- `GET /emails` - List all stored emails
- `GET /emails/<id>/attachments` - List attachments for a specific email
- `GET /attachments/<id>/download` - Download a specific attachment

## Development

- The application uses SQLite for data storage (`emails.db`)
- Emails are uniquely identified by their Message-ID
- Attachments are stored in the database as binary data
- The application checks for new emails every 30 seconds
- Detailed logging is provided for email processing status

## Error Handling

The application includes robust error handling for:
- IMAP connection issues
- Database operations
- Email processing errors
- Duplicate email detection

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
