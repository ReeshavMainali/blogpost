# Slated - A Minimalist Blogging Platform

A clean, minimal space to read and write. No noise — just words.

Slated is a modern blogging platform built with Flask that focuses on simplicity and readability. Share your ideas, discover great writers, and engage with the community.

## Features

### Core Features
- [x] User authentication (registration, login, logout)
- [x] Create, edit, and delete blog posts with markdown support
- [x] Cover image uploads for posts
- [x] User profiles with bio and profile pictures
- [x] Responsive design for mobile and desktop

### Content Discovery
- [x] Trending posts sorted by views and likes
- [x] Recent posts feed
- [x] Search functionality for posts and writers
- [x] Pagination for trending posts and search results (10 items per page)

### Engagement Features
- [x] Like/unlike posts
- [x] Comment on posts with reply functionality
- [x] Delete your own comments
- [x] View count tracking

### View Tracking
- [x] Authenticated users can view a post once per account
- [x] Unauthenticated users tracked via cookies (one view per post per 30 days)
- [x] View counts contribute to trending algorithm

### User Features
- [x] User settings page
- [x] Profile customization (bio, profile picture)
- [x] View your own posts
- [x] Manage your account

### UI/UX
- [x] Dark/light theme toggle
- [x] Clean, minimalist interface
- [x] Smooth transitions and hover effects
- [x] Markdown editor with live preview
- [x] Icon-based stats (views, likes, comments)

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Markdown**: Flask-Markdown
- **Authentication**: Werkzeug security utilities

## Setup Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository or navigate to the project directory:
```bash
cd blogpost
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:

**On Linux/macOS:**
```bash
source .venv/bin/activate
```

**On Windows:**
```bash
.venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables (optional):
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///blog.db
```

6. Run the application:
```bash
python app.py
```

The app will start at `http://localhost:5000`

## Project Structure

```
blogpost/
├── app.py                 # Flask app initialization
├── config.py              # Configuration settings
├── models.py              # Database models (User, Post, Like, Comment, View)
├── requirements.txt       # Python dependencies
├── routes/                # Route handlers
│   ├── auth.py           # Authentication routes
│   ├── blog.py           # Blog and search routes
│   └── user.py           # User profile routes
├── templates/            # HTML templates
│   ├── base.html         # Base template with navbar
│   ├── auth/             # Login/register pages
│   ├── blog/             # Blog pages (index, post, editor, search)
│   └── user/             # User pages (profile, settings)
├── static/               # Static files
│   ├── src/              # CSS source
│   ├── dist/             # Compiled CSS
│   └── uploads/          # User uploads (images)
└── utils.py              # Utility functions
```

## Database Models

### User
- Authentication and profile information
- Relationship to posts, likes, comments, and views

### Post
- Blog post content with markdown support
- Cover image, title, slug, and metadata
- Relationships to likes, comments, and views

### Like
- Tracks user likes on posts
- One like per user per post constraint

### Comment
- Nested comments with reply functionality
- Supports parent-child relationships

### View
- Tracks authenticated user views on posts
- One view per user per post constraint

## Configuration

Key settings in `config.py`:

- `MAX_CONTENT_LENGTH`: File upload size limit (4MB default)
- `UPLOAD_FOLDER`: Location for uploaded files
- `ALLOWED_EXTENSIONS`: Image file types allowed (png, jpg, jpeg, gif, webp)
- `SQLALCHEMY_DATABASE_URI`: Database connection string

## Usage

### Creating a Post
1. Click the "+ Write" button (requires login)
2. Enter title and content in markdown
3. Optionally add a cover image
4. Click publish

### Searching
1. Use the search bar in the navbar
2. Search for post titles/content or writer usernames
3. Results are paginated with 10 items per page

### Engagement
1. Like posts by clicking the heart icon
2. Comment on posts with nested reply support
3. View counts update automatically on page load

### Profile
1. Click your profile picture in the navbar
2. View your posted content
3. Visit settings to update bio and profile picture

## Performance

- Trending algorithm combines views and likes
- Database indexes on frequently queried fields
- Cookie-based view tracking for unauthenticated users
- Efficient pagination with SQL limits

## Security Features

- Password hashing with werkzeug
- CSRF protection via Flask-Login
- User authorization checks on post/comment operations
- Input validation and sanitization

## Browser Compatibility

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Future Enhancements

Potential features for future development:
- [ ] Bookmarks/reading list
- [ ] Categories/tags
- [ ] Email notifications
- [ ] Social media sharing
- [ ] API endpoints
- [ ] Dark mode persistence
- [ ] Post scheduling
- [ ] Analytics dashboard

## Troubleshooting

### Request Size Limit Error
If you get a "request exceeds size limit" error, increase `MAX_CONTENT_LENGTH` in `config.py`:
```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### Database Issues
To reset the database:
```bash
rm blog.db
python app.py  # Will recreate on startup
```

### Missing Uploads Folder
The application automatically creates the uploads folder on startup.

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, check the code comments or review the route implementations in the `routes/` directory.
