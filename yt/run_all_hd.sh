cd /home/claude/travel
for s in "$@"; do python3 yt/render_hd.py $s >> yt/hd_$s.log 2>&1; echo "FINISHED $s" >> yt/hd_$s.log; done
