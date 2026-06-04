class UserModel {
  final int id;
  final String email;
  final String? name;
  final bool isConfirmed;

  UserModel({
    required this.id,
    required this.email,
    this.name,
    required this.isConfirmed,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      email: json['email'] as String,
      name: json['name'] as String?,
      isConfirmed: json['is_confirmed'] as bool? ?? true,
    );
  }
}

class ProfileModel {
  final String? name;
  final String? gender;
  final int? age;
  final double? weight;
  final double? height;
  final double? activityLevel;
  final double? dailyTarget;
  final int waterTarget;
  final int stepsTarget;
  final String? mood;
  final int waterMl;
  final int score;
  final int streakDays;
  final bool isPremium;

  ProfileModel({
    this.name,
    this.gender,
    this.age,
    this.weight,
    this.height,
    this.activityLevel,
    this.dailyTarget,
    this.waterTarget = 2000,
    this.stepsTarget = 10000,
    this.mood,
    this.waterMl = 0,
    this.score = 0,
    this.streakDays = 0,
    this.isPremium = false,
  });

  bool get isComplete =>
      name != null &&
      gender != null &&
      age != null &&
      weight != null &&
      height != null &&
      activityLevel != null;

  factory ProfileModel.fromJson(Map<String, dynamic> json) {
    return ProfileModel(
      name: json['name'] as String?,
      gender: json['gender'] as String?,
      age: json['age'] as int?,
      weight: (json['weight'] as num?)?.toDouble(),
      height: (json['height'] as num?)?.toDouble(),
      activityLevel: (json['activity_level'] as num?)?.toDouble(),
      dailyTarget: (json['daily_target'] as num?)?.toDouble(),
      waterTarget: json['water_target'] as int? ?? 2000,
      stepsTarget: json['steps_target'] as int? ?? 10000,
      mood: json['mood'] as String?,
      waterMl: json['water_ml'] as int? ?? 0,
      score: json['score'] as int? ?? 0,
      streakDays: json['streak_days'] as int? ?? 0,
      isPremium: json['is_premium'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toUpdateJson() => {
        if (name != null) 'name': name,
        if (gender != null) 'gender': gender,
        if (age != null) 'age': age,
        if (weight != null) 'weight': weight,
        if (height != null) 'height': height,
        if (activityLevel != null) 'activity_level': activityLevel,
        if (waterTarget != 2000) 'water_target': waterTarget,
        if (stepsTarget != 10000) 'steps_target': stepsTarget,
        if (mood != null) 'mood': mood,
      };
}

class MealModel {
  final int? id;
  final String foodName;
  final double weightGrams;
  final double calories;
  final double protein;
  final double fat;
  final double carbs;
  final String date;
  final String? time;

  MealModel({
    this.id,
    required this.foodName,
    required this.weightGrams,
    required this.calories,
    this.protein = 0,
    this.fat = 0,
    this.carbs = 0,
    required this.date,
    this.time,
  });

  factory MealModel.fromJson(Map<String, dynamic> json) {
    return MealModel(
      id: json['id'] as int?,
      foodName: json['food_name'] as String,
      weightGrams: (json['weight_grams'] as num).toDouble(),
      calories: (json['calories'] as num).toDouble(),
      protein: (json['protein'] as num?)?.toDouble() ?? 0,
      fat: (json['fat'] as num?)?.toDouble() ?? 0,
      carbs: (json['carbs'] as num?)?.toDouble() ?? 0,
      date: json['date'] as String,
      time: json['time'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'food_name': foodName,
        'weight_grams': weightGrams,
        'calories': calories,
        'protein': protein,
        'fat': fat,
        'carbs': carbs,
        'date': date,
        if (time != null) 'time': time,
      };
}

class NutritionResult {
  final double calories;
  final double protein;
  final double fat;
  final double carbs;

  NutritionResult({
    required this.calories,
    required this.protein,
    required this.fat,
    required this.carbs,
  });

  factory NutritionResult.fromJson(Map<String, dynamic> json) {
    final n = json['nutrition'] as Map<String, dynamic>;
    return NutritionResult(
      calories: (n['calories'] as num).toDouble(),
      protein: (n['protein'] as num?)?.toDouble() ?? 0,
      fat: (n['fat'] as num?)?.toDouble() ?? 0,
      carbs: (n['carbs'] as num?)?.toDouble() ?? 0,
    );
  }
}

class ChatMessage {
  final String role;
  final String content;
  final DateTime time;

  ChatMessage({required this.role, required this.content, DateTime? time})
      : time = time ?? DateTime.now();
}
