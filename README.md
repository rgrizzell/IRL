# Grizz's Intelligent Rack Lighting

IRL is a silly little project that was started to add some intelligent lighting to a server rack enclosure.

# Connecting to a CircuitPython Device
Use the `screen` utility to make a serial connection.
```shell
screen /dev/ttyACM0 115200
```

## Permissions
In some cases, permissions may prevent access to the device.
```text
$ ls -l /dev/ttyACM0 
crw-rw---- 1 root dialout 166, 0 Aug 29 11:13 /dev/ttyACM0
```

Use the following command to add the current user to the correct socket group.
```shell
sudo usermod $USER -aG dailout
```
**Log out and log back in to inherit the new group.**


# Server Serial Testing
To emulate a serial connection for testing, run the following command
```shell
socat -d -d pty,raw,echo=0 pty,raw,echo=0 &
```
```text
2021/02/22 19:27:45 socat[12233] N PTY is /dev/pts/1
2021/02/22 19:27:45 socat[12233] N PTY is /dev/pts/2
2021/02/22 19:27:45 socat[12233] N starting data transfer loop with FDs [5,5] and [7,7]
```
Then attach a terminal to one of the sockets.
```shell
cat </dev/pty/2
```
Start the server with the other socket.
```shell
./server.py --usb='/dev/pty/1'
```

Any serial commands sent by the server will show up.