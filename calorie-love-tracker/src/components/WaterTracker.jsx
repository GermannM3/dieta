import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";
import { Droplets, Plus, Minus } from "lucide-react";

export const WaterTracker = ({ user, onWaterUpdate }) => {
  const [waterAmount, setWaterAmount] = useState(user?.water_ml || 0);
  const [loading, setLoading] = useState(false);

  const dailyGoal = user?.water_target || 2000;
  const progressPercentage = Math.min((waterAmount / dailyGoal) * 100, 100);

  const updateWater = async (newAmount) => {
    if (!user) return;
    
    setLoading(true);
    try {
      const { error } = await supabase
        .from("profiles")
        .update({ water_ml: Math.max(0, newAmount) })
        .eq("user_id", user.user_id);

      if (error) throw error;

      setWaterAmount(Math.max(0, newAmount));
      onWaterUpdate?.(Math.max(0, newAmount));
      
    } catch (error) {
      toast({
        title: "Ошибка",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addWater = (ml) => {
    updateWater(waterAmount + ml);
  };

  const handleInputChange = (e) => {
    const value = parseInt(e.target.value) || 0;
    updateWater(value);
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Droplets className="h-5 w-5 text-blue-500" />
          Вода
        </CardTitle>
        <CardDescription>
          Цель: {dailyGoal} мл в день
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Выпито</span>
            <span>{waterAmount} мл</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
          <div className="text-xs text-muted-foreground text-center">
            {Math.round(progressPercentage)}% от дневной нормы
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Input
            type="number"
            value={waterAmount}
            onChange={handleInputChange}
            disabled={loading}
            className="flex-1"
            min="0"
            step="50"
          />
          <span className="text-sm text-muted-foreground">мл</span>
        </div>

        <div className="grid grid-cols-4 gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={loading}
            onClick={() => addWater(250)}
            className="flex flex-col gap-1 h-auto py-2"
          >
            <Plus className="h-3 w-3" />
            <span className="text-xs">250 мл</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={loading}
            onClick={() => addWater(500)}
            className="flex flex-col gap-1 h-auto py-2"
          >
            <Plus className="h-3 w-3" />
            <span className="text-xs">500 мл</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={loading}
            onClick={() => addWater(-250)}
            className="flex flex-col gap-1 h-auto py-2"
          >
            <Minus className="h-3 w-3" />
            <span className="text-xs">-250 мл</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={loading}
            onClick={() => updateWater(0)}
            className="flex flex-col gap-1 h-auto py-2"
          >
            <span className="text-xs">Сброс</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};