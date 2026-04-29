# Sky Engineering Portal

A web-based application for Sky's Engineering Department to discover, 
contact, and visualise engineering teams and their dependencies.

Built with Django 6, Python, SQLite, Bootstrap 5.

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/W1947717-AV/Engineering-Portal.git
cd Engineering-Portal

### 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

### 3. Install dependencies
pip install -r requirements.txt

### 4. Apply database migrations
python manage.py migrate

### 5. Create a superuser (admin access)
python manage.py createsuperuser

### 6. Run the development server
python manage.py runserver

Then open http://127.0.0.1:8000 in your browser.

## Running Tests
python manage.py test

## Project Structure

| App | Responsibility |
|---|---|
| `teams` | Teams directory, departments, search, dependencies |
| `messages_app` | Internal messaging (inbox, sent, drafts) |
| `schedule_app` | Meeting scheduling and management |
| `dashboard_app` | Dashboard, user registration, authentication |

## Admin Panel

Access at http://127.0.0.1:8000/admin/ using your superuser credentials.

## Tech Stack

- **Backend:** Django 6, Python 3.13
- **Database:** SQLite
- **Frontend:** Bootstrap 5.3, HTML, CSS
