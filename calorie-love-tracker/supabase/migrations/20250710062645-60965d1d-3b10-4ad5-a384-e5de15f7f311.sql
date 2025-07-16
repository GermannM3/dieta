-- Add customizable targets to profiles table
ALTER TABLE public.profiles 
ADD COLUMN water_target INTEGER DEFAULT 2000 CHECK (water_target > 0),
ADD COLUMN steps_target INTEGER DEFAULT 10000 CHECK (steps_target > 0);