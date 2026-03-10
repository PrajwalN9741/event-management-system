# MNNMP Events – Event Management System (EMS)

MNNMP Events is a professional, high-performance Event Management System designed to streamline inventory tracking, quotation generation, and team management. Built with Flask and enhanced with PWA capabilities, it offers a premium user experience for event professionals.

## 🚀 Key Features

- **Dashboard**: Real-time overview of current, upcoming, and past events with a clean, modern UI.
- **Inventory Stack**: A visual tracking system that shows available vs. allocated stock using dynamic progress bars.
- **Quick Edit**: Instant modal-based editing for inventory items without page reloads.
- **User Management**: Unified portal for administrators to manage staff, roles, and access.
- **Quotation System**: Professional PDF generation for event quotations, including client signatures and flower arrangements.
- **Email Integration**: Direct SMTP integration to send PDF quotations and event confirmations to clients.
- **PWA Ready**: Installable on mobile and desktop as a Progressive Web App for a native app feel.

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- Pip (Python package manager)

### 2. Clone the Project
```bash
git clone <repository-url>
cd ems1
```

### 3. Create a Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configuration (.env)
Create a `.env` file in the root directory (copy from `.env.example` if available) and configure your environment variables:
```env
SECRET_KEY=your_secret_key_here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=MNNMP Events <your-email@gmail.com>
```
*Note: For Gmail, use an [App Password](https://myaccount.google.com/apppasswords).*

### 6. Initialize Database
The application automatically creates the SQLite database and a default admin user on the first run.
- **Default Username**: `admin`
- **Default Password**: `Admin@123`

### 7. Run the Application
```bash
python app.py
```
The app will be available at: `http://localhost:5000`

## 📁 Project Structure

- `app.py`: Main application entry point and configuration.
- `models.py`: SQLAlchemy database models (User, Event, Inventory, Quotation).
- `routes/`: Blueprint-based routing logic for different modules.
- `templates/`: Jinja2 HTML templates using Bootstrap 5.
- `static/`: Static assets (CSS, JS, Images, PWA manifest).
- `utils/`: Helper functions for PDF generation and Emailing.

## 📱 PWA Instructions
To install the app on your device:
1. Open the app in a modern browser (Chrome/Edge/Safari).
2. Look for the "Install" icon in the address bar or select "Add to Home Screen" from the browser menu.
3. The app will appear on your desktop/mobile home screen with the MNNMP logo.

## 📝 License
Proprietary documentation and software for MNNMP Events.
