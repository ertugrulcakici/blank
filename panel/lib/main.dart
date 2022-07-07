import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:panel/core/cache/locale_manager.dart';
import 'package:panel/view/home/view/home_view.dart';

void main(List<String> args) {
  LocaleManager.instance.prefrencesInit().then((value) {
    runApp(const App());
  });
}

class App extends StatelessWidget {
  const App({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ProviderScope(
      child: ScreenUtilInit(
          designSize: const Size(1920, 1080),
          builder: (context, widget) => const MaterialApp(home: HomeView())),
    );
  }
}
