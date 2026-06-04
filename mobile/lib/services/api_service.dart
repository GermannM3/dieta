import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/models.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

class ApiService {
  ApiService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;
  String? _token;

  void setToken(String? token) => _token = token;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Uri _uri(String path) {
    final base = AppConfig.apiUrl.replaceAll(RegExp(r'/+$'), '');
    final p = path.startsWith('/') ? path : '/$path';
    return Uri.parse('$base$p');
  }

  Future<Map<String, dynamic>> _handle(http.Response response) async {
    Map<String, dynamic> body = {};
    if (response.body.isNotEmpty) {
      try {
        body = jsonDecode(response.body) as Map<String, dynamic>;
      } catch (_) {
        body = {'detail': response.body};
      }
    }
    if (response.statusCode >= 400) {
      throw ApiException(
        body['detail']?.toString() ?? 'Ошибка сервера (${response.statusCode})',
        statusCode: response.statusCode,
      );
    }
    return body;
  }

  Future<Map<String, dynamic>> register(String email, String password, {String? name}) async {
    final res = await _client.post(
      _uri('/auth/register'),
      headers: _headers,
      body: jsonEncode({'email': email, 'password': password, if (name != null) 'name': name}),
    );
    return _handle(res);
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    final res = await _client.post(
      _uri('/auth/login'),
      headers: _headers,
      body: jsonEncode({'email': email, 'password': password}),
    );
    return _handle(res);
  }

  Future<UserModel> me() async {
    final res = await _client.get(_uri('/auth/me'), headers: _headers);
    final data = await _handle(res);
    return UserModel.fromJson(data);
  }

  Future<ProfileModel> getProfile() async {
    final res = await _client.get(_uri('/web/profile'), headers: _headers);
    final data = await _handle(res);
    return ProfileModel.fromJson(data['profile'] as Map<String, dynamic>);
  }

  Future<ProfileModel> updateProfile(Map<String, dynamic> payload) async {
    final res = await _client.put(
      _uri('/web/profile'),
      headers: _headers,
      body: jsonEncode(payload),
    );
    final data = await _handle(res);
    return ProfileModel.fromJson(data['profile'] as Map<String, dynamic>);
  }

  Future<List<MealModel>> getMeals({String? date}) async {
    final uri = date != null
        ? _uri('/web/meals').replace(queryParameters: {'date': date})
        : _uri('/web/meals');
    final res = await _client.get(uri, headers: _headers);
    final data = await _handle(res);
    return (data['meals'] as List)
        .map((e) => MealModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> addMeal(MealModel meal) async {
    final res = await _client.post(
      _uri('/web/meals'),
      headers: _headers,
      body: jsonEncode(meal.toJson()),
    );
    await _handle(res);
  }

  Future<void> deleteMeal(int id) async {
    final res = await _client.delete(_uri('/web/meals/$id'), headers: _headers);
    await _handle(res);
  }

  Future<List<Map<String, dynamic>>> searchFood(String query) async {
    final res = await _client.post(
      _uri('/search_food'),
      headers: _headers,
      body: jsonEncode({'query': query}),
    );
    final data = await _handle(res);
    return (data['foods'] as List).cast<Map<String, dynamic>>();
  }

  Future<NutritionResult> calculateCalories(String foodName, double weightGrams) async {
    final res = await _client.post(
      _uri('/calculate_calories'),
      headers: _headers,
      body: jsonEncode({'food_name': foodName, 'weight_grams': weightGrams}),
    );
    final data = await _handle(res);
    return NutritionResult.fromJson(data);
  }

  Future<int> updateWater(int amountMl) async {
    final res = await _client.post(
      _uri('/web/water'),
      headers: _headers,
      body: jsonEncode({'amount_ml': amountMl}),
    );
    final data = await _handle(res);
    return data['total_water'] as int;
  }

  Future<Map<String, dynamic>> getStats() async {
    final res = await _client.get(_uri('/web/stats'), headers: _headers);
    final data = await _handle(res);
    return data['stats'] as Map<String, dynamic>;
  }

  Future<String> askDietolog(String message, List<Map<String, String>> history) async {
    final res = await _client.post(
      _uri('/web/dietolog'),
      headers: _headers,
      body: jsonEncode({'message': message, 'history': history}),
    );
    final data = await _handle(res);
    return data['response'] as String;
  }

  Future<bool> healthCheck() async {
    try {
      final res = await _client.get(_uri('/health'));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
