This is a database of the vast majority of the Jeopdary! games played, as gathered
by J! Archive (www.j-archive.com) and scraped by me. This data is not affiliated with 
Jeopardy! in any way.

Init'ing the db:
1. Create a database in mysql
2. cat j.sql into mysql as whichever user you want 
3. edit parsegame.py's connect string

Loading the games:
1. run getj.sh

TODO:
* make this usable by others
* add command line options to getj.sh, parsegame.py
* make the producer/consumer model work over a network socket to avoid the GIL problems
* switch to a SAX parser for speed


jGameData's schema is licensed under a Creative Commons Attribution-ShareAlike 
3.0 Unported License.

JGameData's parsing code is under the BSD license; see license.txt for more
information.
