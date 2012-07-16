kiosk
=====

A musical information Kiosk powered by [The Echo Nest](http://the.echonest.com/) from 1984 to run on your Apple //c. It will only show information about bands from 1984 or before.

![Moby](https://p.twimg.com/AxZGm8vCEAAxATm.jpg:small)

# How

1. Get an Apple //c, a USB-serial adaptor, and an
[Apple //c serial cable, floppy with ATD Pro on it and two blank floppies from Retrofloppy](http://retrofloppy.com/products.html)
2. Install [Modem MGR](http://mirrors.apple2.org.za/ground.icaen.uiowa.edu/apple8/Comm/Modem.mgr/) using ATD Pro on
the two blank floppies.
3. [Read this guide to set up Modem MGR for vt220, 1200 baud 8n1](http://pdw.weinstein.org/2007/06/apple-hacking-for-fun-and-profit.html)
4. Turn on the //c with the Modem MGR program disk in. Hit Esc, then colon, then a V for VT220.
5. On your mac or linux box, hook up the USB serial adaptor, install the drivers, open an 80x24 terminal window and run

    screen /dev/tty.usbserial 1200
(Note that your tty might be named something else depending on device, like /dev/tty.PL2303)
6. Now hit control-A, then a colon, then type

    exec ::: /usr/libexec/getty std.1200
7. The Apple //c should show your login for your computer. Type your password, etc from your //c.
8. Run python kiosk.py for "interactive" mode and python kiosk.py auto for an auto slideshow mode of artists.

Remember to change _THE_YEAR_IS if you don't like 1984.


