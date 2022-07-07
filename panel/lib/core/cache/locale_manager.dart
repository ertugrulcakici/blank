import 'package:panel/product/enums/locale_enums.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LocaleManager {
  static final LocaleManager _instance = LocaleManager._init();
  SharedPreferences? _preferences;
  static LocaleManager get instance => _instance;

  LocaleManager._init();

  Future prefrencesInit() async {
    instance._preferences ??= await SharedPreferences.getInstance();
  }

  bool? getBool(LocaleEnum key) => _preferences!.getBool(key.name);
  double? getDouble(LocaleEnum key) => _preferences!.getDouble(key.name);
  int? getInt(LocaleEnum key) => _preferences!.getInt(key.name);
  String? getString(LocaleEnum key) => _preferences!.getString(key.name);
  List<String>? getStringList(String key) => _preferences!.getStringList(key);
  dynamic get(LocaleEnum key) => _preferences!.get(key.name);

  Future<bool> setBool(LocaleEnum key, bool value) async =>
      await _preferences!.setBool(key.name, value);
  Future<bool> setDouble(LocaleEnum key, double value) async =>
      await _preferences!.setDouble(key.name, value);
  Future<bool> setInt(LocaleEnum key, int value) async =>
      await _preferences!.setInt(key.name, value);
  Future<bool> setString(LocaleEnum key, String value) async =>
      await _preferences!.setString(key.name, value);
  Future<bool> setStringList(LocaleEnum key, List<String> value) async =>
      await _preferences!.setStringList(key.name, value);

  Future<bool> setDynamicString(
          LocaleEnum key, String prefix, String value) async =>
      await _preferences!.setString("${key.name}$prefix", value);

  Future<String?> getDynamicString(LocaleEnum key, String prefix) async =>
      _preferences!.getString("${key.name}$prefix");

  Future<bool> clear() async => await _preferences!.clear();
  Future<bool> remove(LocaleEnum key) async =>
      await _preferences!.remove(key.name);

  bool containsKey(LocaleEnum key) => _preferences!.containsKey(key.name);
}
