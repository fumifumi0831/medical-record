-- Create storage bucket for medical record images
INSERT INTO storage.buckets (id, name) VALUES ('images', 'images')
ON CONFLICT DO NOTHING;

-- Set up public access policy for the images bucket
CREATE POLICY "Public Access" ON storage.objects FOR SELECT USING (bucket_id = 'images');

-- Create medical_records table
CREATE TABLE IF NOT EXISTS public.medical_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  original_image_url TEXT NOT NULL,
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processing_status TEXT DEFAULT 'pending'
);

-- Create extracted_data table
CREATE TABLE IF NOT EXISTS public.extracted_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  record_id UUID NOT NULL REFERENCES public.medical_records(id) ON DELETE CASCADE,
  extracted_text TEXT,
  extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_medical_records_uploaded_at ON public.medical_records(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_extracted_data_record_id ON public.extracted_data(record_id);

-- Enable RLS (Row Level Security)
ALTER TABLE public.medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.extracted_data ENABLE ROW LEVEL SECURITY;

-- Create policies for anonymous access (since we don't need authentication for this app)
CREATE POLICY "Anonymous select medical_records" ON public.medical_records
  FOR SELECT USING (true);

CREATE POLICY "Anonymous insert medical_records" ON public.medical_records
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anonymous update medical_records" ON public.medical_records
  FOR UPDATE USING (true);

CREATE POLICY "Anonymous select extracted_data" ON public.extracted_data
  FOR SELECT USING (true);

CREATE POLICY "Anonymous insert extracted_data" ON public.extracted_data
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anonymous update extracted_data" ON public.extracted_data
  FOR UPDATE USING (true);
