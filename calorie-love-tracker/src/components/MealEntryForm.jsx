import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { Plus, Search } from "lucide-react";

const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000')
  .replace(/\/$/, '');

export const MealEntryForm = ({ user, onMealAdded }) => {
  const [foodName, setFoodName] = useState("");
  const [foodSuggestions, setFoodSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [calories, setCalories] = useState('');
  const [weight, setWeight] = useState('');
  const [nutrition, setNutrition] = useState(null);

  const handleFoodNameChange = async (value) => {
    setFoodName(value);
    if (value.length > 2) {
      try {
        const response = await fetch(`${API_BASE}/search_food`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: value })
        });
        
        if (response.ok) {
          const data = await response.json();
          setFoodSuggestions(data.foods.map(food => food.name));
        }
      } catch (error) {
        console.error('Ошибка поиска продуктов:', error);
      }
    } else {
      setFoodSuggestions([]);
    }
  };

  const selectFood = async (foodName) => {
    setFoodName(foodName);
    setShowSuggestions(false);
    await updateCalories(foodName, weight);
  };

  const updateCalories = async (foodName, weight) => {
    if (!foodName || !weight) return;
    
    try {
      const response = await fetch(`${API_BASE}/calculate_calories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          food_name: foodName, 
          weight_grams: parseFloat(weight) 
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setCalories(data.nutrition.calories.toFixed(0));
        setNutrition(data.nutrition);
      } else {
        setCalories('Нет данных');
        setNutrition(null);
      }
    } catch (error) {
      console.error('Ошибка расчета калорий:', error);
      setCalories('Нет данных');
      setNutrition(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setLoading(true);

    try {
      if (calories === 'Нет данных') {
        toast({
          title: "Ошибка",
          description: "Не удалось рассчитать калории для данного продукта",
          variant: "destructive",
        });
        setLoading(false);
        return;
      }

      if (user) {
        // Зарегистрированный пользователь
        const { data: { user: authUser } } = await supabase.auth.getUser();
        if (!authUser) throw new Error("Пользователь не авторизован");

        const { error } = await supabase
          .from("meals")
          .insert({
            user_id: authUser.id,
            food_name: foodName,
            weight_grams: parseFloat(weight),
            calories: parseFloat(calories),
            protein: nutrition?.protein || 0,
            fat: nutrition?.fat || 0,
            carbs: nutrition?.carbs || 0,
            time: new Date().toTimeString().slice(0, 5),
            date: new Date().toISOString().split('T')[0]
          });

        if (error) throw error;
      } else {
        // Гость - сохраняем в localStorage
        const sessionMeals = JSON.parse(localStorage.getItem('guestMeals') || '[]');
        const newMeal = {
          id: Date.now().toString(),
          food_name: foodName,
          weight_grams: parseFloat(weight),
          calories: parseFloat(calories),
          protein: nutrition?.protein || 0,
          fat: nutrition?.fat || 0,
          carbs: nutrition?.carbs || 0,
          time: new Date().toTimeString().slice(0, 5),
          date: new Date().toISOString().split('T')[0]
        };
        sessionMeals.push(newMeal);
        localStorage.setItem('guestMeals', JSON.stringify(sessionMeals));
      }

      setFoodName("");
      setWeight("");
      setCalories('Нет данных');
      setNutrition(null);

      toast({ title: "Прием пищи добавлен!" });
      onMealAdded?.();
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

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="h-5 w-5 text-primary" />
          Добавить прием пищи
        </CardTitle>
        <CardDescription>
          Введите название продукта и его вес. Калории рассчитает ИИ-диетолог
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2 relative">
            <Label htmlFor="food">Продукт</Label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                id="food"
                value={foodName}
                onChange={(e) => {
                  const newValue = e.target.value;
                  setFoodName(newValue);
                  handleFoodNameChange(newValue);
                  updateCalories(newValue, weight);
                }}
                onFocus={() => setShowSuggestions(true)}
                placeholder="Начните вводить название продукта..."
                className="pl-10"
                required
              />
              {showSuggestions && foodSuggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-background border rounded-md shadow-lg max-h-40 overflow-y-auto">
                  {foodSuggestions.map((food, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => selectFood(food)}
                      className="w-full px-4 py-2 text-left hover:bg-accent hover:text-accent-foreground"
                    >
                      {food}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="weight">Вес (граммы)</Label>
              <Input
                id="weight"
                type="number"
                step="0.1"
                value={weight}
                onChange={(e) => {
                  const newWeight = e.target.value;
                  setWeight(newWeight);
                  updateCalories(foodName, newWeight);
                }}
                required
                min="0.1"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="time">Время</Label>
              <Input
                id="time"
                type="time"
                value={new Date().toTimeString().slice(0, 5)}
                onChange={(e) => {}}
                required
              />
            </div>
          </div>

          {foodName && weight && nutrition && (
            <div className="p-4 bg-accent/10 rounded-lg space-y-2">
              <p className="text-sm font-medium text-primary">
                📊 Пищевая ценность (ИИ-диетолог):
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                <div>
                  <span className="text-muted-foreground">🔥 Калории:</span>
                  <span className="font-semibold ml-1">{nutrition.calories.toFixed(0)} ккал</span>
                </div>
                <div>
                  <span className="text-muted-foreground">🥩 Белки:</span>
                  <span className="font-semibold ml-1">{nutrition.protein.toFixed(1)} г</span>
                </div>
                <div>
                  <span className="text-muted-foreground">🧈 Жиры:</span>
                  <span className="font-semibold ml-1">{nutrition.fat.toFixed(1)} г</span>
                </div>
                <div>
                  <span className="text-muted-foreground">🍞 Углеводы:</span>
                  <span className="font-semibold ml-1">{nutrition.carbs.toFixed(1)} г</span>
                </div>
              </div>
            </div>
          )}

          <Button 
            type="submit" 
            className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90" 
            disabled={loading}
          >
            {loading ? "Добавление..." : "Добавить прием пищи"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};