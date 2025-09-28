# Fix: Video Bucket Setup Guide

## The Problem
You're getting a 400 Bad Request error because the "video" bucket doesn't exist in your Supabase Storage.

## Solution: Create the Video Bucket

### Method 1: Using Supabase Dashboard (Recommended)

1. **Go to your Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Select your project: `xmpxayzxdowmaoytdbgs`

2. **Navigate to Storage**
   - Click on "Storage" in the left sidebar
   - You should see an empty storage section

3. **Create New Bucket**
   - Click "New bucket" button
   - **Bucket name**: `video` (exactly this name)
   - **Public bucket**: ✅ Check this box (allows public access)
   - Click "Create bucket"

4. **Set Bucket Policies (Important!)**
   - After creating the bucket, click on the "video" bucket
   - Go to "Policies" tab
   - Click "New Policy"
   - Choose "For full customization"
   - Add this policy:

   ```sql
   -- Allow public uploads
   CREATE POLICY "Allow public uploads" ON storage.objects
   FOR INSERT WITH CHECK (bucket_id = 'video');
   
   -- Allow public reads
   CREATE POLICY "Allow public reads" ON storage.objects
   FOR SELECT USING (bucket_id = 'video');
   ```

### Method 2: Using SQL Editor

1. **Go to SQL Editor**
   - In your Supabase dashboard, click "SQL Editor"
   - Click "New query"

2. **Run this SQL**:
   ```sql
   -- Create the video bucket
   INSERT INTO storage.buckets (id, name, public)
   VALUES ('video', 'video', true);
   
   -- Create policies for the bucket
   CREATE POLICY "Allow public uploads" ON storage.objects
   FOR INSERT WITH CHECK (bucket_id = 'video');
   
   CREATE POLICY "Allow public reads" ON storage.objects
   FOR SELECT USING (bucket_id = 'video');
   ```

3. **Click "Run"** to execute the SQL

## Verify the Setup

After creating the bucket, you can verify it works by:

1. **Check in Storage Dashboard**
   - Go to Storage → you should see "video" bucket listed

2. **Test Upload**
   - Try recording a video in your app
   - Check browser console for success messages
   - The upload should now work!

## Troubleshooting

### If you still get errors:

1. **Check bucket name**: Must be exactly `video` (lowercase)
2. **Check permissions**: Make sure the bucket is public
3. **Check policies**: Ensure the policies are created correctly
4. **Check API key**: Verify your environment variables are correct

### Common Error Messages:

- `"Bucket not found"` → Bucket doesn't exist, create it
- `"Permission denied"` → Bucket policies not set up correctly
- `"Invalid API key"` → Check your environment variables

## Next Steps

Once the bucket is created:
1. Your video uploads will work automatically
2. Videos will be stored in Supabase Storage
3. Metadata will be saved to the database
4. You'll get public URLs for each video

The app will now successfully upload your 10-second videos! 🎉
