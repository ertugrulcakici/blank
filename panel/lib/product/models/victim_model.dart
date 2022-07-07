import 'dart:async';
import 'dart:developer';
import 'dart:io';
import 'dart:typed_data';

class VictimModel {
  Socket soket;
  String? name;

  VictimModel(this.soket, Function notifyListeners) {
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
      log("$ip:$endpoint:$error");
      try {
        _subscription!.cancel();
      } catch (e) {
        log("Stream kapatma hatası: $e");
      }
      _subscription = null;
    });

    // done
    _subscription!.onDone(() {
      log("$ip:$endpoint:done");
      _subscription!.cancel();
      _subscription = null;
    });
  }

  String get ip => soket.remoteAddress.address;
  int get endpoint => soket.remotePort;

  StreamSubscription? _subscription;
}
