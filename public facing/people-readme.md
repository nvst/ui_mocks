# People/Biography Django App Implementation Guide

This guide will help you implement the people/biography functionality for your Ethical Capital website using Django's author system integrated with the Dewey design system.

## Overview

The people app provides:
- Individual biography pages for team members
- A team listing page
- Integration with Django's author system
- PDF bio downloads
- Admin interface for easy content management
- Responsive design following the Dewey design system

## Installation Steps

### 1. Create the Django App

```bash
python manage.py startapp people
```

### 2. Add to INSTALLED_APPS

In your `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'people',
]
```

### 3. Configure Media Files

In `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

In your main `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your patterns
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4. Copy the Model Files

Copy the provided models, views, and admin configurations to your `people` app directory.

### 5. Run Migrations

```bash
python manage.py makemigrations people
python manage.py migrate
```

### 6. Create Templates Directory

Create the following directory structure:
```
templates/
  people/
    person_detail.html
    people_list.html
    person_bio_pdf.html
  base.html
```

### 7. Install PDF Generation (Optional)

If you want PDF bio downloads:

```bash
pip install pdfkit
# Also install wkhtmltopdf on your system
# Mac: brew install wkhtmltopdf
# Ubuntu: sudo apt-get install wkhtmltopdf
```

### 8. Add URL Patterns

Include the people URLs in your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('', include('people.urls')),
]
```

## Customization

### Adding Custom Fields

To add custom fields to the Person model:

```python
# In models.py
class Person(models.Model):
    # ... existing fields
    custom_field = models.CharField(max_length=200, blank=True)
```

Then run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Styling Adjustments

The templates use CSS variables from the Dewey design system. You can override these in your base template:

```css
:root {
    --ec-purple: #553C9A;  /* Your brand color */
    --ec-purple-light: #6B46C1;
    /* ... other variables */
}
```

### Template Customization

The templates are designed to be easily customizable. Key sections:

1. **Biography Content**: Uses Django's `safe` filter for HTML content
2. **Stats Bar**: Shows key metrics about the person
3. **Timeline**: Professional experience displayed chronologically
4. **Publications**: Automatically sorted by date

## Content Management

### Using the Admin Interface

1. Go to `/admin/` and log in
2. Navigate to "People" section
3. Add/edit team members
4. Use inline forms for positions, credentials, publications

### Content Guidelines

- **Biography**: Write in HTML format, use `<p>` tags for paragraphs
- **Philosophy Quote**: A single impactful quote about their approach
- **Photos**: Upload square images (recommended 600x600px minimum)
- **Tags**: Use for filtering on the people list page

## Integration with Django Auth

The Person model includes an optional link to Django's User model:

```python
# To link a person to a user account
from django.contrib.auth.models import User

user = User.objects.get(username='sloaneortel')
person = Person.objects.get(slug='sloane-ortel')
person.user = user
person.save()
```

This allows you to:
- Use Django's permission system
- Link blog posts or other content to people
- Enable user-specific features

## URL Structure

The app creates these URLs:
- `/people/` - Team listing page
- `/people/sloane-ortel/` - Individual bio page
- `/people/sloane-ortel/download/` - PDF download

## Sample Data

To populate sample data:

```bash
python manage.py populate_sample_people
```

## Troubleshooting

### Images not showing
- Check MEDIA_URL and MEDIA_ROOT settings
- Ensure media files are being served in development
- Verify file permissions

### PDF generation fails
- Ensure wkhtmltopdf is installed
- Check path configuration for pdfkit
- Try with a simple HTML template first

### Slug conflicts
- Slugs must be unique
- The model auto-generates slugs from names
- Manually set slugs in admin if needed

## Security Considerations

- Set appropriate permissions for bio editing
- Sanitize HTML content in biographies
- Use Django's CSRF protection on forms
- Limit file upload sizes for photos

## Performance Optimization

- Use `select_related()` and `prefetch_related()` in views
- Cache rendered bio pages
- Optimize images before upload
- Consider pagination for large teams

## Future Enhancements

Consider adding:
- Blog post authorship
- Team member availability status
- Skills/expertise taxonomy
- Multi-language support
- Social media feed integration