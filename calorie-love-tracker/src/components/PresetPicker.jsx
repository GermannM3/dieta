import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";
import { ChefHat, Plus, Trash2, Coffee, UtensilsCrossed, Cookie } from "lucide-react";
import quickPresets from "@/lib/presets.json";
import { getFoodCalories, searchFood } from '../lib/foodData';

const mealIcons = {
  breakfast: Coffee,
  lunch: UtensilsCrossed,
  dinner: UtensilsCrossed,
  snack: Cookie
};

const mealLabels = {
  breakfast: "Завтрак",
  lunch: "Обед", 
  dinner: "Ужин",
  snack: "Перекус"
};

export const PresetPicker = ({ user, onPresetSelected }) => {
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newPreset, setNewPreset] = useState({
    name: "",
    meal_type: "breakfast",
    food_items: []
  });

  useEffect(() => {
    if (user) {
      loadPresets();
    }
  }, [user]);

  const loadPresets = async () => {
    try {
      const { data, error } = await supabase
        .from("presets")
        .select("*")
        .eq("user_id", user.user_id)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setPresets(data || []);
    } catch (error) {
      console.error("Error loading presets:", error);
    }
  };

  const addQuickPreset = async (preset) => {
    if (!user) return;
    
    setLoading(true);
    try {
      const today = new Date().toISOString().split("T")[0];
      const time = new Date().toLocaleTimeString("ru-RU", { hour12: false });

      const entries = preset.items.map((item) => ({
        user_id: user.user_id,
        date: today,
        time: time,
        food_name: item.name,
        weight_grams: item.grams,
        calories: item.kcal,
      }));

      const { error } = await supabase.from("meals").insert(entries);
      if (error) throw error;

      toast({
        title: "Набор добавлен",
        description: `"${preset.title}" добавлен в дневник`,
      });
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

  const createPreset = async () => {
    if (!newPreset.name.trim() || newPreset.food_items.length === 0) {
      toast({
        title: "Ошибка",
        description: "Заполните название и добавьте хотя бы один продукт",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const totalCalories = newPreset.food_items.reduce((sum, item) => sum + item.calories, 0);
      
      const { error } = await supabase
        .from("presets")
        .insert({
          user_id: user.user_id,
          name: newPreset.name,
          meal_type: newPreset.meal_type,
          food_items: newPreset.food_items,
          total_calories: totalCalories
        });

      if (error) throw error;

      toast({
        title: "Пресет создан",
        description: `"${newPreset.name}" добавлен в ваши шаблоны`,
      });

      setNewPreset({ name: "", meal_type: "breakfast", food_items: [] });
      setCreateDialogOpen(false);
      loadPresets();
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

  const deletePreset = async (presetId) => {
    setLoading(true);
    try {
      const { error } = await supabase
        .from("presets")
        .delete()
        .eq("id", presetId);

      if (error) throw error;

      toast({
        title: "Пресет удален",
        description: "Шаблон успешно удален",
      });

      loadPresets();
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

  const selectPreset = (preset) => {
    onPresetSelected?.(preset);
    toast({
      title: "Пресет выбран",
      description: `Добавлен "${preset.name}" (${preset.total_calories} ккал)`,
    });
  };

  const addFoodItem = () => {
    setNewPreset(prev => ({
      ...prev,
      food_items: [...prev.food_items, { name: "", weight: 100, calories: 0 }]
    }));
  };

  const updateFoodItem = async (index, field, value) => {
    setNewPreset(prev => ({
      ...prev,
      food_items: prev.food_items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const removeFoodItem = (index) => {
    setNewPreset(prev => ({
      ...prev,
      food_items: prev.food_items.filter((_, i) => i !== index)
    }));
  };

  if (!user) return null;

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <ChefHat className="h-5 w-5" />
          Готовые наборы
        </CardTitle>
        <CardDescription>
          Быстро добавляйте свои любимые комбинации блюд
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Быстрые пресеты из JSON */}
        <div className="grid gap-2 mb-4">
          <h3 className="text-sm font-medium text-muted-foreground">Готовые наборы</h3>
          <div className="flex flex-wrap gap-2">
            {quickPresets.map((preset) => (
              <Button
                key={preset.title}
                size="sm"
                variant="outline"
                onClick={() => addQuickPreset(preset)}
                disabled={loading}
                className="text-xs"
              >
                {preset.title}
              </Button>
            ))}
          </div>
        </div>

        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Создать новый пресет
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Новый пресет</DialogTitle>
              <DialogDescription>
                Создайте шаблон для быстрого добавления блюд
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="preset-name">Название</Label>
                <Input
                  id="preset-name"
                  value={newPreset.name}
                  onChange={(e) => setNewPreset(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Мой завтрак"
                />
              </div>
              
              <div className="space-y-2">
                <Label>Тип приема пищи</Label>
                <Select value={newPreset.meal_type} onValueChange={(value) => setNewPreset(prev => ({ ...prev, meal_type: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(mealLabels).map(([value, label]) => (
                      <SelectItem key={value} value={value}>{label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label>Продукты</Label>
                  <Button size="sm" variant="outline" onClick={addFoodItem}>
                    <Plus className="h-3 w-3" />
                  </Button>
                </div>
                
                {newPreset.food_items.map((item, index) => (
                  <div key={index} className="flex gap-2 items-center">
                    <Input
                      placeholder="Название"
                      value={item.name}
                      onChange={(e) => updateFoodItem(index, 'name', e.target.value)}
                      className="flex-1"
                    />
                    <Input
                      type="number"
                      placeholder="Вес"
                      value={item.weight}
                      onChange={(e) => updateFoodItem(index, 'weight', parseInt(e.target.value) || 0)}
                      className="w-20"
                    />
                    <Input
                      type="number"
                      placeholder="Ккал"
                      value={item.calories}
                      onChange={(e) => updateFoodItem(index, 'calories', parseInt(e.target.value) || 0)}
                      className="w-20"
                    />
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeFoodItem(index)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>

              <Button onClick={createPreset} disabled={loading} className="w-full">
                Создать пресет
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        <div className="grid gap-2">
          {presets.map((preset) => {
            const Icon = mealIcons[preset.meal_type] || ChefHat;
            return (
              <div
                key={preset.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Icon className="h-4 w-4" />
                  <div>
                    <div className="font-medium">{preset.name}</div>
                    <div className="text-sm text-muted-foreground flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {mealLabels[preset.meal_type]}
                      </Badge>
                      <span>{preset.total_calories} ккал</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => selectPreset(preset)}
                    disabled={loading}
                  >
                    Выбрать
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => deletePreset(preset.id)}
                    disabled={loading}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            );
          })}
          
          {presets.length === 0 && (
            <div className="text-center py-6 text-muted-foreground">
              <ChefHat className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>Пока нет сохраненных пресетов</p>
              <p className="text-sm">Создайте первый шаблон!</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};