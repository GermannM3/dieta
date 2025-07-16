-- Add mood, water tracking and streak fields to profiles table
ALTER TABLE public.profiles 
ADD COLUMN mood TEXT CHECK (mood IN ('excellent', 'good', 'okay', 'bad', 'terrible')),
ADD COLUMN water_ml INTEGER DEFAULT 0 CHECK (water_ml >= 0),
ADD COLUMN streak_days INTEGER DEFAULT 0 CHECK (streak_days >= 0);

-- Create presets table for meal templates
CREATE TABLE public.presets (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')) NOT NULL,
  food_items JSONB NOT NULL,
  total_calories DECIMAL(7,2) NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security for presets
ALTER TABLE public.presets ENABLE ROW LEVEL SECURITY;

-- Create policies for presets
CREATE POLICY "Users can view their own presets" 
ON public.presets 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own presets" 
ON public.presets 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own presets" 
ON public.presets 
FOR UPDATE 
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own presets" 
ON public.presets 
FOR DELETE 
USING (auth.uid() = user_id);

-- Create trigger for automatic timestamp updates on presets
CREATE TRIGGER update_presets_updated_at
BEFORE UPDATE ON public.presets
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Create indexes for better performance
CREATE INDEX idx_presets_user_id ON public.presets(user_id);
CREATE INDEX idx_presets_meal_type ON public.presets(meal_type);