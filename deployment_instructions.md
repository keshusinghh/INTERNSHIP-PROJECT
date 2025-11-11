# Deployment Instructions for NexusBoard

## Deploying to Render.com

1. **Create a Render Account**
   - Go to [Render.com](https://render.com/) and sign up for a free account

2. **Connect Your GitHub Repository**
   - Push your code to a GitHub repository
   - In Render dashboard, click "New" and select "Web Service"
   - Connect your GitHub account and select your repository

3. **Configure Your Web Service**
   - Name: `nexusboard` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Select the free plan

4. **Set Environment Variables**
   - Add the following environment variables:
     - `SECRET_KEY`: Generate a random string
     - `DATABASE_URL`: This will be provided by Render or you can use your own PostgreSQL database URL

5. **Deploy Your Application**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Your application will be available at `https://your-service-name.onrender.com`

## Accessing Your Application

- **Regular Users**: Visit the homepage and use the Register/Login functionality
- **Admin Access**: Click the Admin button and login with:
  - Username: `admin`
  - Password: `team3`

## Features Implemented

1. **Team Chat**: Users can communicate with each other through the Team Chat feature
2. **Admin Dashboard**: Admins can monitor user activities and tasks
3. **User Activity Tracking**: All task additions, modifications, and deletions are tracked with timestamps