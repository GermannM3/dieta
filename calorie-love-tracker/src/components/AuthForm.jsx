import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";

export const AuthForm = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        
        console.log("Успешный вход:", data);
        toast({ title: "Добро пожаловать!" });
        onAuthSuccess();
      } else {
        // Регистрация БЕЗ подтверждения email
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/`,
            data: {
              email_confirm: false // Отключаем подтверждение
            }
          }
        });
        
        if (error) throw error;
        
        console.log("Результат регистрации:", data);
        
        // Проверяем, нужно ли подтверждение
        if (data.user && !data.session) {
          toast({ 
            title: "Проверьте email", 
            description: "Мы отправили письмо с подтверждением. Проверьте папку спам.",
            variant: "default"
          });
        } else if (data.session) {
          // Если сессия создана сразу - регистрация прошла успешно
          toast({ title: "Регистрация успешна! Добро пожаловать!" });
          onAuthSuccess();
        } else {
          // Другие случаи
          toast({ 
            title: "Регистрация отправлена", 
            description: "Проверьте email для завершения регистрации"
          });
        }
      }
    } catch (error) {
      console.error("Ошибка аутентификации:", error);
      
      let errorMessage = error.message;
      
      // Переводим основные ошибки на русский
      if (error.message.includes("Invalid login credentials")) {
        errorMessage = "Неверный email или пароль";
      } else if (error.message.includes("User already registered")) {
        errorMessage = "Пользователь с таким email уже зарегистрирован";
      } else if (error.message.includes("Password should be at least")) {
        errorMessage = "Пароль должен содержать минимум 6 символов";
      } else if (error.message.includes("Unable to validate email address")) {
        errorMessage = "Некорректный формат email";
      } else if (error.message.includes("Email not confirmed")) {
        errorMessage = "Email не подтвержден. Проверьте почту и нажмите на ссылку подтверждения.";
      }
      
      toast({
        title: "Ошибка",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    try {
      // Вход под демо-аккаунтом
      const { data, error } = await supabase.auth.signInWithPassword({
        email: "demo@example.com",
        password: "demo123456",
      });
      
      if (error) {
        // Если демо-аккаунт не существует, создаем его
        if (error.message.includes("Invalid login credentials")) {
          const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
            email: "demo@example.com",
            password: "demo123456",
            options: {
              data: {
                email_confirm: false
              }
            }
          });
          
          if (signUpError) throw signUpError;
          
          if (signUpData.session) {
            toast({ title: "Демо-аккаунт создан! Добро пожаловать!" });
            onAuthSuccess();
          } else {
            throw new Error("Не удалось создать демо-аккаунт");
          }
        } else {
          throw error;
        }
      } else {
        toast({ title: "Вход в демо-режиме успешен!" });
        onAuthSuccess();
      }
    } catch (error) {
      console.error("Ошибка демо-входа:", error);
      toast({
        title: "Ошибка демо-входа",
        description: "Попробуйте зарегистрироваться вручную",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary/10 via-accent/5 to-info/10">
      <Card className="w-full max-w-md shadow-card-hover">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            🥗 Трекер Калорий
          </CardTitle>
          <CardDescription>
            {isLogin ? "Войдите в аккаунт" : "Создайте аккаунт"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAuth} className="space-y-4">
            <div className="space-y-2">
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Input
                type="password"
                placeholder="Пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button 
              type="submit" 
              className="w-full" 
              disabled={loading}
            >
              {loading ? "Загрузка..." : (isLogin ? "Войти" : "Зарегистрироваться")}
            </Button>
          </form>
          
          {/* Кнопка демо-входа */}
          <div className="mt-4">
            <Button 
              onClick={handleDemoLogin}
              variant="outline"
              className="w-full"
              disabled={loading}
            >
              🎭 Демо-вход (без регистрации)
            </Button>
          </div>
          
          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-primary hover:underline"
            >
              {isLogin ? "Нет аккаунта? Зарегистрируйтесь" : "Есть аккаунт? Войдите"}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};