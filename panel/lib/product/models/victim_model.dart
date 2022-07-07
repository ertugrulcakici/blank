import 'dart:async';
import 'dart:developer';
import 'dart:io';
import 'dart:typed_data';

class VictimModel {
  Socket soket;
  String? name;
  Function notifyListeners;
  bool _active = true;
  bool get active => _active;
  set active(bool value) {
    _active = value;
    _subscription?.cancel();
    _subscription = null;
    notifyListeners();
  }

  VictimModel(this.soket, this.notifyListeners) {
    _subscription = soket.listen((data) {});

    // data
    _subscription!.onData((data) {
      if (name == null) {
        name = String.fromCharCodes(data).replaceAll(" ", "");
        notifyListeners();
      } else {
        log("Bilinmeyen data geldi: ${String.fromCharCodes(data as Uint8List)}");
      }
      notifyListeners();
    });

    // error
    _subscription!.onError((error) {
      log("$ip:$endpoint error:$error");
      active = false;
    });

    // done
    _subscription!.onDone(() {
      log("$ip:$endpoint:done");
      active = false;
    });
  }

  Future send(String data) async {
    if (active) {
      try {
        soket.write(data);
      } catch (e) {
        log("Gönderme hatası: $e");
        active = false;
      }
    }
  }

  String get ip => soket.remoteAddress.address;
  int get endpoint => soket.remotePort;

  StreamSubscription? _subscription;
}
