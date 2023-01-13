testfiles=`ls *.test`
testfilesAliceQualichain=`ls *.test_alice_qual`


for eachfile in $testfiles
do
   echo $eachfile
done

python3 evaluation.py $testfiles $testfilesAliceQualichain plot1
python3 evaluation.py $testfiles $testfilesAliceQualichain plot2
python3 evaluation.py $testfiles $testfilesAliceQualichain plot3
