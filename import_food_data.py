import os
import csv
import psycopg2
from dotenv import load_dotenv
import time
from tqdm import tqdm

load_dotenv()

def get_file_line_count(file_path):
    """Подсчитывает количество строк в файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f) - 1  # -1 для заголовка

def import_food_csv():
    """Импортирует данные из food.csv с прогресс-баром"""
    print("🍽️ Начинаем импорт таблицы food...")
    
    db_url = os.getenv('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    file_path = 'fooddata_tmp/FoodData_Central_csv_2025-04-24/food.csv'
    
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не найден!")
        return False
    
    total_lines = get_file_line_count(file_path)
    print(f"📊 Всего строк для импорта: {total_lines:,}")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            imported = 0
            
            with tqdm(total=total_lines, desc="Импорт food") as pbar:
                for row in reader:
                    try:
                        batch.append((
                            int(row['fdc_id']), 
                            row['description'], 
                            row.get('food_category_id'), 
                            row.get('data_type')
                        ))
                    except (ValueError, KeyError) as e:
                        print(f"⚠️ Ошибка в строке: {e}")
                        continue
                    
                    if len(batch) >= 1000:  # Уменьшил размер батча для стабильности
                        try:
                            cur.executemany(
                                'INSERT INTO food (fdc_id, description, food_category_id, data_type) VALUES (%s, %s, %s, %s) ON CONFLICT (fdc_id) DO NOTHING', 
                                batch
                            )
                            imported += len(batch)
                            conn.commit()
                            pbar.update(len(batch))
                            batch = []
                        except Exception as e:
                            print(f"❌ Ошибка при вставке батча: {e}")
                            conn.rollback()
                            batch = []
                
                # Вставляем оставшиеся записи
                if batch:
                    try:
                        cur.executemany(
                            'INSERT INTO food (fdc_id, description, food_category_id, data_type) VALUES (%s, %s, %s, %s) ON CONFLICT (fdc_id) DO NOTHING', 
                            batch
                        )
                        imported += len(batch)
                        conn.commit()
                        pbar.update(len(batch))
                    except Exception as e:
                        print(f"❌ Ошибка при вставке последнего батча: {e}")
                        conn.rollback()
        
        print(f"✅ Импорт food завершён! Импортировано: {imported:,} записей")
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка при импорте food: {e}")
        return False

def import_food_nutrient_csv():
    """Импортирует данные из food_nutrient.csv с прогресс-баром"""
    print("🥗 Начинаем импорт таблицы food_nutrient...")
    
    db_url = os.getenv('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    file_path = 'fooddata_tmp/FoodData_Central_csv_2025-04-24/food_nutrient.csv'
    
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не найден!")
        return False
    
    total_lines = get_file_line_count(file_path)
    print(f"📊 Всего строк для импорта: {total_lines:,}")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            imported = 0
            
            with tqdm(total=total_lines, desc="Импорт food_nutrient") as pbar:
                for row in reader:
                    try:
                        batch.append((
                            int(row['id']), 
                            int(row['fdc_id']), 
                            int(row['nutrient_id']), 
                            float(row['amount'])
                        ))
                    except (ValueError, KeyError) as e:
                        print(f"⚠️ Ошибка в строке: {e}")
                        continue
                    
                    if len(batch) >= 1000:  # Уменьшил размер батча
                        try:
                            cur.executemany(
                                'INSERT INTO food_nutrient (id, fdc_id, nutrient_id, amount) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING', 
                                batch
                            )
                            imported += len(batch)
                            conn.commit()
                            pbar.update(len(batch))
                            batch = []
                        except Exception as e:
                            print(f"❌ Ошибка при вставке батча: {e}")
                            conn.rollback()
                            batch = []
                
                # Вставляем оставшиеся записи
                if batch:
                    try:
                        cur.executemany(
                            'INSERT INTO food_nutrient (id, fdc_id, nutrient_id, amount) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING', 
                            batch
                        )
                        imported += len(batch)
                        conn.commit()
                        pbar.update(len(batch))
                    except Exception as e:
                        print(f"❌ Ошибка при вставке последнего батча: {e}")
                        conn.rollback()
        
        print(f"✅ Импорт food_nutrient завершён! Импортировано: {imported:,} записей")
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка при импорте food_nutrient: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск импорта данных FoodData Central в Neon PostgreSQL")
    print("=" * 60)
    
    start_time = time.time()
    
    # Импортируем food.csv
    food_success = import_food_csv()
    
    if food_success:
        print("\n" + "=" * 60)
        # Импортируем food_nutrient.csv
        nutrient_success = import_food_nutrient_csv()
        
        if nutrient_success:
            end_time = time.time()
            duration = end_time - start_time
            print(f"\n🎉 Импорт завершён успешно за {duration:.2f} секунд")
        else:
            print("\n❌ Импорт food_nutrient не удался")
    else:
        print("\n❌ Импорт food не удался")
    
    print("\n📊 Проверяем результат...")
    os.system("python check_db_status.py") 