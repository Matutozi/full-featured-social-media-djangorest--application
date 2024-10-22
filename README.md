## Django Rest Framework (DRF) Social Media Application

This is a full-featured social media application built using **Django Rest Framework (DRF)**. It includes features like user authentication, profiles, posts, followers, messaging, notifications, and more. The project is designed with scalability and modern web technologies, providing a comprehensive backend system for a social media platform.

## Key Features

### User Authentication:
- [x] User registration, login, and logout.
- [x] Password hashing using Django's authentication system.
- [x] JWT token-based authentication.
- [ ] Role-based access control (e.g., admin and regular user).

### User Profiles:
- [x] Create, update, and delete profiles.
- [x] Support for profile pictures and cover photos.
- [ ] Bio, contact information, and social links.

### Posts & Feeds:
- [x] Create, edit, and delete posts (text, images, and videos).
- [x] Like, comment, and share functionality.
- [x] Real-time feed updates using Django Channels (for WebSocket).

### Followers & Following:
- [x] Follow/unfollow functionality.
- [x] Notifications for follows and follow-backs.
- [x] Display follower and following lists.

### Notifications:
- [x] In-app notifications for likes, comments, shares, and follows.
- [x] Real-time notifications using Server-Sent Events (SSE).
- [ ] Notification settings and preferences.

### Messaging:
- [x] Real-time private messaging between users using Django Channels.
- [x] Group chats and chat rooms.
- [ ] File sharing within chats (images, documents, etc.).

### Search & Discovery:
- [x] Search users, posts, hashtags, and keywords.
- [x] Trending topics and suggested users to follow.
- [x] Tagging users in posts and comments.

### Admin Panel:
- [ ] User management (view, ban, unban users).
- [ ] Content moderation (flagged posts, reported users).
- [ ] Analytics and dashboard for site activity.

---

## Requirements

### Documentation & Testing:
- [ ] API documentation using tools like Postman or Swagger.
- [ ] Comprehensive testing suite using `unittest` and `DRF’s` testing utilities.

### Database:
- [ ] PostgreSQL database for storing application data.
- [ ] Robust schema design to handle relationships and indexing.

### Caching:
- [ ] Implement caching for frequently accessed data using Redis.
- [ ] Use background tasks for cache invalidation.

### Deployment:
- [ ] Docker containerization for easy deployment.
- [ ] CI/CD pipelines for automated testing and deployment.
- [ ] Cloud deployment using AWS, GCP, Azure, or any other provider.

### Security:
- [ ] Best security practices such as CORS, CSRF protection, and input validation.
- [ ] Regular security audits and penetration testing.

### Error Handling:
- [ ] Endpoints return appropriate error responses and status codes.
- [ ] Graceful error handling to prevent server crashes.

---

## Technologies Used

- **Django Rest Framework (DRF):** The main framework for building the API.
- **PostgreSQL:** Relational database for storing data.
- **Redis:** For caching frequently accessed data and background tasks.
- **Django Channels:** For handling real-time features such as WebSockets.
- **Celery:** For background task processing.
- **Docker:** For containerization and deployment.
- **unittest:** For testing the application.

---

## Getting Started

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/<username>/full-featured-social-media-djangorest--application.git
   cd full-featured-social-media-djangorest--application
   ```

2. **Set Up Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server:**

   ```bash
   python manage.py runserver
   ```

6. **Access the Application:**

   The application will be running at `http://127.0.0.1:8000/`.

---

This project will challenge you to integrate advanced features, providing a comprehensive learning experience in building complex backend systems with **Django Rest Framework**.

