#!/bin/bash

for i in {1..3575}; do
 echo $i
 #curl http://www.j-archive.com/showgame.php?game_id=${i} > games/game_${i}.html & 
 curl http://www.j-archive.com/showgameresponses.php?game_id=${i} > games/game_responses_${i}.html & 
 if [ $((i % 15 )) -eq 0 ];
 then
    sleep 2
 fi
done

