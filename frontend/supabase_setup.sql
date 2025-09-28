-- Create videos table to store video metadata
CREATE TABLE IF NOT EXISTS videos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  filename TEXT NOT NULL,
  url TEXT NOT NULL,
  duration INTEGER NOT NULL, -- duration in seconds
  size BIGINT NOT NULL, -- file size in bytes
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id TEXT DEFAULT 'anonymous',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on uploaded_at for faster queries
CREATE INDEX IF NOT EXISTS idx_videos_uploaded_at ON videos(uploaded_at DESC);

-- Create an index on user_id for user-specific queries
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows anyone to insert videos (for now)
CREATE POLICY "Allow public video uploads" ON videos
  FOR INSERT WITH CHECK (true);

-- Create a policy that allows anyone to read videos (for now)
CREATE POLICY "Allow public video reads" ON videos
  FOR SELECT USING (true);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update updated_at
CREATE TRIGGER update_videos_updated_at 
  BEFORE UPDATE ON videos 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();
