# BitBio Django

A comprehensive Django web application for biological calculations and user management with PDF and EXCEL generation capabilities.

## 🚀 Project Overview

BitBio Django is a modern web application built with Django that provides:

- **User Management System**: Complete user registration, authentication, and approval workflow
- **Biological Calculator**: Advanced calculations with PDF export functionality
- **Admin Interface**: Customized Django admin with enhanced security and domain management
- **PDF Generation**: Automated PDF creation using Playwright for high-quality document output
- **Excel Export**: Data export capabilities using openpyxl

## 🛠️ Tech Stack

### Backend

- **Python 3.8+** - Core programming language
- **Django 5.2.4** - Web framework
- **MySQL** - Database (with mysqlclient driver)
- **ASGI** - Asynchronous server gateway interface

### Key Dependencies

- **Playwright 1.48.0** - PDF generation and browser automation
- **Pillow 10.4.0** - Image processing
- **openpyxl 3.1.5** - Excel file handling
- **sqlparse 0.5.3** - SQL parsing utilities

### Frontend

- **HTML5/CSS3** - Modern web standards
- **JavaScript** - Interactive functionality
- **Custom Fonts** - BitBioSans and Avenir Next LT Pro
- **Responsive Design** - Mobile-friendly interface

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- MySQL server
- Git

### Step 1: Clone the Repository

```bash
cd bitbio-django
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The setup automatically installs Playwright browser dependencies. If you encounter issues, run manually:

```bash
python -m playwright install chromium
python -m playwright install-deps
```

### Step 4: Database Setup

1. Create MySQL database:

```sql
CREATE DATABASE bit_bio_django CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Update database credentials in `bitbio/settings.py` if needed:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "bit_bio_django",
        "USER": "your_username",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "3306",
    }
}
```

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 🚀 Production Setup

For production deployment, follow these steps:

### Step 1: Create Virtual Environment

```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment

```bash
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Database Migrations

```bash
python manage.py migrate
```

### Step 5: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Production Configuration

Before deploying to production, ensure you have:

1. Set `DEBUG = False` in `bitbio/settings.py`
2. Configure production database credentials
3. Set a secure `SECRET_KEY`
4. Configure `ALLOWED_HOSTS` for your domain
5. Set up proper static file serving (Apache/Nginx)
6. Configure HTTPS/SSL certificates

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory for sensitive configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=mysql://user:password@localhost:3306/bit_bio_django
```

### Custom Management Commands

The project includes several custom management commands:

- **User Management**:

  ```bash
  python manage.py create_admin
  python manage.py create_email_superuser
  python manage.py create_test_user
  ```

- **Database Operations**:
  ```bash
  python manage.py check_tables #you can check the tables list
  python manage.py drop_tables  #this will drop all the tables from database
  ```

## 📱 Features

### User Management

- User registration and authentication
- Approval workflow for new users
- Custom user models and forms
- Domain-based access control

### Calculator

- Biological calculations and formulas
- PDF export functionality
- Excel data export
- User profile management

### Admin Interface

- Customized Django admin
- Enhanced security middleware
- Domain management tools
- User approval system

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG = False` in settings
2. Configure production database
3. Set up static file serving
4. Configure HTTPS
5. Set secure `SECRET_KEY`
6. Configure `ALLOWED_HOSTS`

### Static Files

```bash
python manage.py collectstatic
```

### Database Backup

```bash
python manage.py dumpdata > backup.json
```

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

## 📚 API Documentation

The application provides RESTful endpoints for:

- User authentication and management
- Calculator operations
- PDF generation
- Data export

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:

- Check the documentation
- Review existing issues
- Contact the development team

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- User management system
- Calculator with PDF export
- Admin interface customization

---

**Built with ❤️ using Django and modern web technologies**
