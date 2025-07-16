-- Add score field to profiles table for gamification
ALTER TABLE public.profiles 
ADD COLUMN score INTEGER DEFAULT 0 CHECK (score >= 0);