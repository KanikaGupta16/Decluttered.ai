import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Video upload function (legacy - for video recording)
export const uploadVideo = async (file: File, fileName: string) => {
  try {
    console.log('Attempting to upload video:', fileName, 'Size:', file.size)
    
    const { data, error } = await supabase.storage
      .from('video')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      })

    if (error) {
      console.error('Supabase upload error:', error)
      throw error
    }

    console.log('Video upload successful:', data)
    return data
  } catch (error) {
    console.error('Error uploading video:', error)
    throw error
  }
}

// Photo upload function for original photos
export const uploadPhoto = async (file: File, fileName: string) => {
  try {
    console.log('Attempting to upload photo:', fileName, 'Size:', file.size)
    
    const { data, error } = await supabase.storage
      .from('used_upload')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      })

    if (error) {
      console.error('Supabase upload error:', error)
      throw error
    }

    console.log('Photo upload successful:', data)
    return data
  } catch (error) {
    console.error('Error uploading photo:', error)
    throw error
  }
}

// Cropped image upload function
export const uploadCroppedImage = async (file: File, fileName: string) => {
  try {
    console.log('Attempting to upload cropped image:', fileName, 'Size:', file.size)
    
    const { data, error } = await supabase.storage
      .from('cropped')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      })

    if (error) {
      console.error('Supabase cropped upload error:', error)
      throw error
    }

    console.log('Cropped image upload successful:', data)
    return data
  } catch (error) {
    console.error('Error uploading cropped image:', error)
    throw error
  }
}

// Check if bucket exists
export const checkBucketExists = async () => {
  try {
    // First try to list all buckets
    const { data: buckets, error: bucketsError } = await supabase.storage.listBuckets()
    
    if (bucketsError) {
      console.error('Error listing buckets:', bucketsError)
      // If we can't list buckets, try direct access to video bucket
      return await checkVideoBucketDirect()
    }
    
    const videoBucket = buckets.find(bucket => bucket.name === 'video')
    console.log('Available buckets:', buckets.map(b => b.name))
    console.log('Video bucket exists in list:', !!videoBucket)
    
    if (videoBucket) {
      return true
    }
    
    // If not found in list, try direct access
    return await checkVideoBucketDirect()
  } catch (error) {
    console.error('Error checking bucket existence:', error)
    return false
  }
}

// Check video bucket by trying to access it directly
const checkVideoBucketDirect = async () => {
  try {
    const { data, error } = await supabase.storage
      .from('video')
      .list('', { limit: 1 })
    
    if (error) {
      console.error('Direct video bucket access error:', error)
      return false
    }
    
    console.log('Video bucket accessible directly:', true)
    return true
  } catch (error) {
    console.error('Error accessing video bucket directly:', error)
    return false
  }
}

// Get public URL for uploaded video
export const getVideoUrl = (fileName: string) => {
  const { data } = supabase.storage
    .from('video')
    .getPublicUrl(fileName)

  return data.publicUrl
}

// Get public URL for uploaded photo
export const getPhotoUrl = (fileName: string) => {
  const { data } = supabase.storage
    .from('used_upload')
    .getPublicUrl(fileName)

  return data.publicUrl
}

// Save photo metadata to database
export const savePhotoMetadata = async (photoData: {
  filename: string;
  url: string;
  size: number;
  user_id?: string;
}) => {
  try {
    const { data, error } = await supabase
      .from('photos')
      .insert([photoData])
      .select()

    if (error) {
      throw error
    }

    return data
  } catch (error) {
    console.error('Error saving photo metadata:', error)
    throw error
  }
}

// Save cropped object data to database
export const saveCroppedObject = async (croppedData: {
  photo_id: string;
  object_name: string;
  confidence: number;
  bounding_box: any;
  cropped_image_url: string;
  estimated_value?: number;
}) => {
  try {
    const { data, error } = await supabase
      .from('cropped')
      .insert([croppedData])
      .select()

    if (error) {
      throw error
    }

    return data
  } catch (error) {
    console.error('Error saving cropped object:', error)
    throw error
  }
}

// Get cropped objects for a photo
export const getCroppedObjects = async (photoId: string) => {
  try {
    const { data, error } = await supabase
      .from('cropped')
      .select('*')
      .eq('photo_id', photoId)
      .order('confidence', { ascending: false })

    if (error) {
      throw error
    }

    return data
  } catch (error) {
    console.error('Error fetching cropped objects:', error)
    throw error
  }
}

// Save listing to database
export const saveListing = async (listingData: {
  photo_id: string;
  cropped_id: string;
  title: string;
  description: string;
  price: number;
  platforms: string[];
  user_id?: string;
}) => {
  try {
    const { data, error } = await supabase
      .from('listings')
      .insert([listingData])
      .select()

    if (error) {
      throw error
    }

    return data
  } catch (error) {
    console.error('Error saving listing:', error)
    throw error
  }
}

// Get all listings for dashboard
export const getListings = async () => {
  try {
    const { data, error } = await supabase
      .from('listings')
      .select(`
        *,
        photos!inner(url),
        cropped!inner(object_name, cropped_image_url)
      `)
      .order('created_at', { ascending: false })

    if (error) {
      throw error
    }

    return data
  } catch (error) {
    console.error('Error fetching listings:', error)
    throw error
  }
}
