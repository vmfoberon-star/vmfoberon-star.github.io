cd /home/claude/travel
for s in vienna13 benelux12 uk11 alps08 paris06 italy03; do python3 yt/render.py $s || echo "FAIL $s"; done
echo ALLDONE
