testNumber = 100
types = 4
testString = ''
file = open('commands/commands-100', 'w')
for j in range(1, types + 1):
    for i in range(0, testNumber):
        testString = testString + 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance TYPE_' + str(j) + ' 2>&1 | tee runners/support/evaluation/perf_'+ str(j) + '_' + str(i) +'.test &&'
testString = testString[:-2]

file.write(testString)
file.close()