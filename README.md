This is a Python3 template for https://lightningbot.tk/.
The lightningbot documentation is at https://lightningbot.tk/doc.

To launch the project, execute :
```./run.sh``` or ```python3 -m mybot```

You can also use `./run.sh 2` to run 2 bots at the same time, or, heck, `./run.sh 14` to run 14 bots, if that's your thing.

Just fill in the move method in the MyBot class !

By default, the game will play in `test` mode. If you want to play in `ranked` mode, you should put your token in the `TOKEN` environment variable, and create your Bot with the `mode='ranked'` parameter.
