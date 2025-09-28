# Supabase Video Upload Setup

This guide will help you set up Supabase for video uploads in your Decluttered.ai application.

## Prerequisites

1. A Supabase account and project
2. A bucket named "video" in your Supabase storage

## Setup Steps

### 1. Create Environment Variables

Create a `.env` file in the `frontend` directory with your Supabase credentials:

```bash
# Create the .env file
touch .env
```

Then edit `.env` and add your actual Supabase credentials:

```env
SUPABASE_PROJECT_URL=your_supabase_project_url_here
ANON_KEY=your_supabase_anon_key_here
```

### 2. Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to Settings > API
3. Copy the following values:
   - **Project URL** → `SUPABASE_PROJECT_URL`
   - **anon public** key → `ANON_KEY`

### 3. Create the Video Bucket

1. In your Supabase dashboard, go to Storage
2. Click "New bucket"
3. Name it `video`
4. Make it public (optional, depending on your use case)
5. Click "Create bucket"

### 4. Create the Videos Database Table

1. In your Supabase dashboard, go to SQL Editor
2. Copy and paste the contents of `supabase_setup.sql` (included in this project)
3. Click "Run" to execute the SQL script

This will create:
- A `videos` table to store video metadata
- Proper indexes for performance
- Row Level Security policies
- Automatic timestamp updates

### 5. Set Bucket Policies (Optional)

If you want to restrict access, you can set up Row Level Security (RLS) policies:

```sql
-- Allow public uploads to video bucket
CREATE POLICY "Allow public uploads" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'video');

-- Allow public reads from video bucket
CREATE POLICY "Allow public reads" ON storage.objects
FOR SELECT USING (bucket_id = 'video');
```

## How It Works

1. **Video Recording**: The app records a 10-second video using the device camera
2. **Upload**: After recording, the video is automatically uploaded to your Supabase `video` bucket
3. **Progress Tracking**: Users see upload progress with a progress bar
4. **Success Confirmation**: A success message appears when upload is complete
5. **Analysis**: After upload, the video is analyzed for objects (mock implementation)

## File Structure

- `src/config/supabase.ts` - Supabase client configuration and upload functions
- `src/components/CameraFeed.tsx` - Main camera component with upload integration

## Features

- ✅ Automatic video upload after recording
- ✅ Upload progress indicator
- ✅ Success/error handling
- ✅ Unique filename generation with timestamps
- ✅ Public URL generation for uploaded videos

## Troubleshooting

### Common Issues

1. **"Invalid API key" error**
   - Check that your `ANON_KEY` is correct
   - Ensure there are no extra spaces or quotes

2. **"Bucket not found" error**
   - Verify the bucket name is exactly `video`
   - Check that the bucket exists in your Supabase project

3. **Upload fails**
   - Check your internet connection
   - Verify Supabase project is active
   - Check browser console for detailed error messages

### Testing

To test the upload functionality:

1. Start the development server: `npm run dev`
2. Navigate to the camera page
3. Record a 10-second video
4. Watch for the upload progress indicator
5. Check your Supabase storage dashboard to see the uploaded video

## Security Notes

- The anon key is safe to use in frontend applications
- Consider implementing user authentication for production use
- Set up appropriate RLS policies based on your security requirements
