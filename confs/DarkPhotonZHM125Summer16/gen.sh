NEVENTSJOB=$(($NEVENTS/$NCPU))
if [ $TASKTYPE = "gen" ]
then
  SIMSTEP="simStep=False"
else
  SIMSTEP="simStep=True"
fi

for I in $(seq 1 $NCPU)
do
  mkdir gen$I
  cp _gen.py gen_cfg.py gen$I/

  cd gen$I
  ../cmssw.sh $GEN_ARCH $GEN_RELEASE gen ncpu=1 maxEvents=$NEVENTSJOB outputFile=gen${I}.root randomizeSeeds=True firstLumi=$FIRSTLUMI firstEvent=$(($NEVENTSJOB*($I-1)+1)) $SIMSTEP $GRIDPACKS_ARG &
  PIDS[$I]=$!
  cd ..

  echo gen${I}/gen${I}.root >> output_files_gen.list
done

for PID in ${PIDS[*]}
do
  wait $PID
done
