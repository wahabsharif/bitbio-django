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

- Docker and Docker Compose
- Git

### Option 1: Docker Installation (Recommended)

#### Development Environment

1. **Clone the Repository**

```bash
git clone <repository-url>
cd bitbio-django
```

2. **Create Environment File**

```bash
# Create .env file with your configuration
cp .env.example .env
# Edit .env with your database credentials and settings
```

3. **Build and Run Development Container**

```bash
# Build the Docker image
docker-compose build

# Run the development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the development environment
docker-compose down
```

4. **Access the Application**

- Development server: `http://localhost:8000`
- Admin interface: `http://localhost:8000/admin`

#### Production Environment

1. **Build and Run Production Container**

```bash
# Build the production image
docker-compose -f docker-compose.prod.yml build

# Run production environment
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production environment
docker-compose -f docker-compose.prod.yml down
```

### Option 2: Manual Installation

#### Prerequisites

- Python 3.8 or higher
- MySQL server
- Git

#### Step 1: Clone the Repository

```bash
cd bitbio-django
```

#### Step 2: Create Virtual Environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The setup automatically installs Playwright browser dependencies. If you encounter issues, run manually:

```bash
python -m playwright install chromium
python -m playwright
```

#### Step 4: Database Setup

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

#### Step 5: Run Migrations

```bash
python manage.py migrate
```

#### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

#### Step 7: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000/`

## 🐳 Docker Management

### Development Commands

```bash
# Start development environment
docker-compose up -d

# Start with logs visible
docker-compose up

# Stop development environment
docker-compose down

# Rebuild and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Execute commands in development container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Access container shell
docker-compose exec web bash

# Remove all containers and volumes
docker-compose down -v
```

### Production Commands

```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Start with logs visible
docker-compose -f docker-compose.prod.yml up

# Stop production environment
docker-compose -f docker-compose.prod.yml down

# Rebuild and start production
docker-compose -f docker-compose.prod.yml up --build -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Execute commands in production container
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Access production container shell
docker-compose -f docker-compose.prod.yml exec web bash

# Restart production service
docker-compose -f docker-compose.prod.yml restart web

# Scale production service (if needed)
docker-compose -f docker-compose.prod.yml up --scale web=2 -d
```

### Docker Image Management

```bash
# Build image without cache
docker-compose build --no-cache

# Build specific service
docker-compose build web

# Remove unused images
docker image prune

# Remove all unused Docker resources
docker system prune -a

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View Docker images
docker images

# Remove specific image
docker rmi <image_id>
```

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

### Docker Deployment Checklist

1. **Pre-deployment Setup**

   - Set `DEBUG = False` in production environment
   - Configure production database credentials
   - Set secure `SECRET_KEY`
   - Configure `ALLOWED_HOSTS` for your domain
   - Set up SSL/HTTPS certificates
   - Configure proper logging

2. **Docker Production Deployment**

```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Deploy production environment
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment status
docker-compose -f docker-compose.prod.yml ps

# Check application health
curl -f http://localhost:8000/ || exit 1
```

3. **Post-deployment Tasks**

```bash
# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Run database migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Set up monitoring and logging
docker-compose -f docker-compose.prod.yml logs -f web
```

### Static Files & Database Management

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic                    # Development
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput  # Production

# Database backup
docker-compose exec web python manage.py dumpdata > backup.json           # Development
docker-compose -f docker-compose.prod.yml exec web python manage.py dumpdata > backup.json  # Production
```

### Troubleshooting Docker Deployment

```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# View detailed logs
docker-compose -f docker-compose.prod.yml logs --tail=100 web

# Access container for debugging
docker-compose -f docker-compose.prod.yml exec web bash

# Restart specific service
docker-compose -f docker-compose.prod.yml restart web

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d

# Check resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

## 🧪 Testing

### Docker Testing

```bash
# Run tests in development container
docker-compose exec web python manage.py test

# Run tests in production container
docker-compose -f docker-compose.prod.yml exec web python manage.py test

# Run specific test module
docker-compose exec web python manage.py test app_users.tests

# Run tests with verbose output
docker-compose exec web python manage.py test --verbosity=2

# Run tests with coverage
docker-compose exec web python manage.py test --keepdb
```

### Manual Testing

```bash
# Run the test suite
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

## 📋 Quick Reference

### Environment Files

- **Development**: Use `docker-compose.yml` with `.env` file
- **Production**: Use `docker-compose.prod.yml` with hardcoded environment variables

### Ports

- **Development**: `http://localhost:8000`
- **Production**: Configured for production domains

### Common Commands

- **Start Development**: `docker-compose up -d`
- **Start Production**: `docker-compose -f docker-compose.prod.yml up -d`
- **View Logs**: `docker-compose logs -f` (dev) or `docker-compose -f docker-compose.prod.yml logs -f` (prod)
- **Access Container**: `docker-compose exec web bash`

---

**Built with ❤️ using Django and modern web technologies**
