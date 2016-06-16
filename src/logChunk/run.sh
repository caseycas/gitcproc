echo "========== nohup  python ghProc.py $1 >> $2.out 2>> $2.err ============"
nohup  python ghProc.py $1 $3 $4 >> ../../evaluation/log_files/$2.out 2>> ../../evaluation/log_files/$2.err
