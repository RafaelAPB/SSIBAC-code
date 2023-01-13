from evaluation_helper import EvaluationHelper
import numpy as np
import matplotlib.pyplot as plt
import sys
import re
import statistics

## Receives as input the list of files to be parsed, and at the end the type of plot to render
# perf_1_1, qualichain_1_1, alice_1_1 => first test of issuing 1 credential. e.g., perf_1_2, second test

#
test_case = "1_CRED"

total_runtime = []
register_did = []
init_agents = []
publish_schema = []

total_runtime_100_c = []
register_did_100_c = []
init_agents_100_c = []
publish_schema_100_c = []

total_runtime_10_c = []
register_did_10_c = []
init_agents_10_c = []
publish_schema_10_c = []

total_runtime_1000_c = []
register_did_1000_c = []
init_agents_1000_c = []
publish_schema_1000_c = []

# connect
conn_alice_tecnico = []
emit_credential = []
conn_alice_qualichain = []
avg_time_per_cred = []

conn_alice_tecnico_10_c = []
emit_credential_10_c = []
conn_alice_qualichain_10_c = []
avg_time_per_cred_10_c = []

conn_alice_tecnico_100_c = []
emit_credential_100_c = []
conn_alice_qualichain_100_c = []
avg_time_per_cred_100_c = []

conn_alice_tecnico_1000_c = []
emit_credential_1000_c = []
conn_alice_qualichain_1000_c = []
avg_time_per_cred_1000_c = []
# startup phase + connecting phase = bootstrap

# happens on the qualichain agent
# access control phase
construct_proof_request_to_alice = []
construct_proof_to_tecnico = []
handle_proof_from_alice = []
eval_access_control = []

construct_proof_request_to_alice_10_c = []
construct_proof_to_tecnico_10_c = []
handle_proof_from_alice_10_c = []
eval_access_control_10_c = []

construct_proof_request_to_alice_100_c = []
construct_proof_to_tecnico_100_c = []
handle_proof_from_alice_100_c = []
eval_access_control_100_c = []

construct_proof_request_to_alice_1000_c = []
construct_proof_to_tecnico_1000_c = []
handle_proof_from_alice_1000_c = []
eval_access_control_1000_c = []

print('Number of arguments:', len(sys.argv), 'arguments.')
arg_list = sys.argv
print('Argument List:', str(arg_list))

# Parsing input files, correspond to all arguments given as input except the last
#perf_type_number; type 1 - 1 cred; type 2 - 10 cred; type 3 - 100; type 4 - 1000

for output_file in arg_list[1:-1]:
    if "perf_1" in output_file or "qualichain" in output_file or "alice" in output_file:
        test_case = "1_CRED"
    elif "perf_2" in output_file:
        test_case = "10_CRED"
    elif "perf_3" in output_file:
        test_case = "100_CRED"
    elif "perf_4" in output_file:
        test_case = "1000_CRED"
    elif "alice" in output_file or "qualichain" in output_file:
        pass
    else:
        print(output_file)
        raise Exception("Filetype not known")
    # print(output_file)
    with open(output_file, "r") as f:
        lines = f.readline()
        for line in f:
            if "EVALUATION| " in line or "EVALUATION-AC|" in line:
                line = line.strip()
                substring = re.search(':(.*)s', line)
                if substring:
                    time = float(substring.group(1))
                    # print(time)
                    # PERFORMANCE AGENT
                    if "Total runtime:" in line:
                        if test_case == "100_CRED":
                            total_runtime_100_c.append(time)
                        elif test_case == "1000_CRED":
                            total_runtime_1000_c.append(time)
                        elif test_case == "10_CRED":
                            total_runtime_10_c.append(time)
                        else:
                            total_runtime.append(time)
                        # print("Total Runtime: ", total_runtime)
                    elif "Register DIDs:" in line:
                        if test_case == "100_CRED":
                            register_did_100_c.append(time)
                        elif test_case == "1000_CRED":
                            register_did_1000_c.append(time)
                        elif test_case == "10_CRED":
                            register_did_10_c.append(time)
                        else:
                            register_did.append(time)
                        # print("Register DIDs: ", register_did)
                    elif "Initialize Agents:" in line:
                        if test_case == "100_CRED":
                            init_agents_100_c.append(time)
                        elif test_case == "1000_CRED":
                            init_agents_1000_c.append(time)
                        elif test_case == "10_CRED":
                            init_agents_10_c.append(time)
                        else:
                            init_agents.append(time)
                        # print("Init Agents: ", init_agents)
                    elif "Publish Schema:" in line:
                        if test_case == "100_CRED":
                            publish_schema_100_c.append(time)
                        elif test_case == "1000_CRED":
                            publish_schema_1000_c.append(time)
                        elif test_case == "10_CRED":
                            publish_schema_10_c.append(time)
                        else:
                            publish_schema.append(time)
                        # print("Publish Schema Duration: ", publish_schema)

                    # CONNECT PHASE
                    elif "Connect Tecnico-Alice:" in line:
                        if test_case == "100_CRED":
                            conn_alice_tecnico_100_c.append(time)
                        elif test_case == "1000_CRED":
                            conn_alice_tecnico_1000_c.append(time)
                        elif test_case == "10_CRED":
                            conn_alice_tecnico_10_c.append(time)
                        else:
                            conn_alice_tecnico.append(time)
                        # print("Connect Alice-IST: ", conn_alice_tecnico)
                    elif "Emitted Credentials:" in line:
                        if test_case == "100_CRED":
                            emit_credential_100_c.append(time)
                        elif test_case == "1000_CRED":
                            emit_credential_1000_c.append(time)
                        elif test_case == "10_CRED":
                            emit_credential_10_c.append(time)
                        else:
                            emit_credential.append(time)
                        # print("Emit Credential: ", emit_credential)
                    elif "Average time per credential:" in line:
                        if test_case == "100_CRED":
                            avg_time_per_cred_100_c.append(time)
                        elif test_case == "1000_CRED":
                            avg_time_per_cred_1000_c.append(time)
                        elif test_case == "10_CRED":
                            avg_time_per_cred_10_c.append(time)
                        else:
                            avg_time_per_cred.append(time)
                        # print("Average time per credencial: ", avg_time_per_cred)
                    elif "Connect Alice-Qualichain" in line:
                        if test_case == "100_CRED":
                            conn_alice_qualichain_100_c.append(time)
                        elif test_case == "1000_CRED":
                            conn_alice_qualichain_1000_c.append(time)
                        elif test_case == "10_CRED":
                            conn_alice_qualichain_10_c.append(time)
                        else:
                            conn_alice_qualichain.append(time)
                        # print("Connect Alice-Qualichain: ", conn_alice_qualichain)

                    # QUALICHAIN AGENT
                    # ACCESS CONTROL PHASE - in this control the number of emited credentials does not matter
                    elif "Construct Proof Request" in line:
                        construct_proof_request_to_alice.append(time)
                    # ALICE AGENT
                    elif "Construct proof to Tecnico" in line:
                        construct_proof_to_tecnico.append(time)
                    # QUALICHAIN AGENT
                    elif "Handling Presentation Proof" in line:
                        handle_proof_from_alice.append(time)

                    # QUALICHAIN AGENT OR OFF CHAIN
                    elif "Evaluating Access Control Request:" in line:
                        eval_access_control.append(time)
                    else:
                        pass

# Technical/Platform evaluation is on performance.py; Access control evaluation is mediated between qualichain.py and
# alice.py, after having credential issued by faber.py (tecnico lisboa)
#LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance TYPE_3  2>&1 | tee runners/support/evaluation/perf_c_3_7.txt && LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance TYPE_3  2>&1 | tee runners/support/evaluation/perf_c_3_8.txt  && LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance TYPE_3  2>&1 | tee runners/support/evaluation/perf_c_3_9.txt && LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance TYPE_3  2>&1 | tee runners/support/evaluation/perf_c_3_10.txt

# Alice has a seed for its DID
# alice_seed = "d_000000000000000000000000290329"
# Alice DID, LkPc1zMqY1JGGjoKiu2kXV

# Evaluation consists of three phases, first 2 happening on performance.py:

# Startup phase:
# # E| Register DIDs => registers 3 DIDs on the VON dev ledger
# # E| Initialize agents
# # E| Publish schema ==> publishes credentials schema

# Connect phase:
# # E| Connect Tecnico-Alice:
# # E| Emit 1 credential
# # E| Connect Alice to Qualichain"

# Access control phase - takes place on qualichain and alice
# # E| Construct proof request
# # E| Construct proof to Tecnico (Alice.py)
# # E| Handling presentation proof of degree from Alice
# # E| Evaluating access control request based on proof

# startup
# register_did = [3.9377]
# init_agents = [16.1302]
# publish_schema = [12.3415]

# connect
# conn_alice_tecnico = [0.1187]
# emit_credential = [1.92]
# conn_alice_qualichain = [0.1060]

# startup phase + connecting phase = bootstrap


# access control phase
# construct_proof_request_to_alice = [1.9476]
# construct_proof_to_tecnico = [1.3897]
# handle_proof_from_alice = [0.0001]
# eval_access_control = [0.0006]

dimensions = len(register_did)
# total_time_control_phase
durations_1_credential = EvaluationHelper(dimensions, total_runtime, register_did, avg_time_per_cred, init_agents,
                                          publish_schema, conn_alice_tecnico, emit_credential,
                                          conn_alice_qualichain, construct_proof_request_to_alice,
                                          construct_proof_to_tecnico, handle_proof_from_alice, eval_access_control)
durations_10_credential = EvaluationHelper(dimensions, total_runtime_10_c, register_did_10_c,
                                           avg_time_per_cred_10_c, init_agents_10_c,
                                           publish_schema_10_c, conn_alice_tecnico_10_c, emit_credential_10_c,
                                           conn_alice_qualichain_10_c, construct_proof_request_to_alice,
                                           construct_proof_to_tecnico, handle_proof_from_alice, eval_access_control)
durations_100_credential = EvaluationHelper(dimensions, total_runtime_100_c, register_did_100_c,
                                            avg_time_per_cred_100_c, init_agents_100_c,
                                            publish_schema_100_c, conn_alice_tecnico_100_c, emit_credential_100_c,
                                            conn_alice_qualichain_100_c, construct_proof_request_to_alice,
                                            construct_proof_to_tecnico, handle_proof_from_alice,
                                            eval_access_control)
durations_1000_credential = EvaluationHelper(dimensions, total_runtime_1000_c, register_did_1000_c,
                                             avg_time_per_cred_1000_c, init_agents_1000_c,
                                             publish_schema_1000_c, conn_alice_tecnico_1000_c,
                                             emit_credential_1000_c,
                                             conn_alice_qualichain_1000_c, construct_proof_request_to_alice,
                                             construct_proof_to_tecnico, handle_proof_from_alice,
                                             eval_access_control)

#print("============= durations_1_credential =================")
#durations_1_credential.print_all()
#print("TOTAL TIME: ", durations_1_credential.get_total_time_mean())
#print("========================================================")
print("============= durations_10_credential =================")
durations_10_credential.print_all()
print("TOTAL TIME: ", durations_10_credential.get_total_time_mean())
#print("========================================================")
#print("============= durations_100_credential =================")
#durations_100_credential.print_all()
#print("TOTAL TIME: ", durations_100_credential.get_total_time_mean())

#print("========================================================")
#print("============= durations_1000_credential =================")
#durations_1000_credential.print_all()
#print("TOTAL TIME: ", durations_1000_credential.get_total_time_mean())
#print("========================================================")

startup_mean = durations_1_credential.get_mean_startup_phase_duration()
startup_mean_10_c = durations_10_credential.get_mean_startup_phase_duration()
startup_mean_100_c = durations_100_credential.get_mean_startup_phase_duration()
startup_mean_1000_c = durations_1000_credential.get_mean_startup_phase_duration()

standard_deviation_startup = durations_1_credential.get_std_dev_startup_phase_duration()
standard_deviation_startup_10_c = durations_10_credential.get_std_dev_startup_phase_duration()
standard_deviation_startup_100_c = durations_100_credential.get_std_dev_startup_phase_duration()
standard_deviation_startup_1000_c = durations_1000_credential.get_std_dev_startup_phase_duration()

connect_mean = durations_1_credential.get_mean_connect_phase_duration()
connect_mean_10_c = durations_10_credential.get_mean_connect_phase_duration()
connect_mean_100_c = durations_100_credential.get_mean_connect_phase_duration()
connect_mean_1000_c = durations_1000_credential.get_mean_connect_phase_duration()

standard_deviation_connect = durations_1_credential.get_std_dev_connect_phase_duration()
standard_deviation_connect_10_c = durations_10_credential.get_std_dev_connect_phase_duration()
standard_deviation_connect_100_c = durations_100_credential.get_std_dev_connect_phase_duration()
standard_deviation_connect_1000_c = durations_1000_credential.get_std_dev_connect_phase_duration()


ac_mean = durations_1_credential.get_mean_ac_phase_duration()
ac_mean_10_c = durations_10_credential.get_mean_ac_phase_duration()
ac_mean_100_c = durations_100_credential.get_mean_ac_phase_duration()
ac_mean_1000_c = durations_1000_credential.get_mean_ac_phase_duration()

standard_deviation_ac = durations_1_credential.get_std_dev_ac_phase_duration()
standard_deviation_ac_10_c = durations_10_credential.get_std_dev_ac_phase_duration()
standard_deviation_ac_100_c = durations_100_credential.get_std_dev_ac_phase_duration()
standard_deviation_ac_1000_c = durations_1000_credential.get_std_dev_ac_phase_duration()

if "plot1" in arg_list:
    labels = ['1 Credential', '10 Credentials', '100 Credentials', '1000 Credentials']
    # https://matplotlib.org/3.2.1/gallery/lines_bars_and_markers/horizontal_barchart_distribution.html#sphx-glr-gallery-lines-bars-and-markers-horizontal-barchart-distribution-py
    startup_means = [startup_mean, startup_mean_10_c, startup_mean_100_c, startup_mean_1000_c]
    startup_standard_deviations = [standard_deviation_startup, standard_deviation_startup_10_c,
                                   standard_deviation_startup_100_c, standard_deviation_startup_1000_c]
    #print ("startup_means")
    #print (startup_means)
    #print ("startup_standard_deviations")
    #print (startup_standard_deviations)

    connect_means = [connect_mean, connect_mean_10_c, connect_mean_100_c, connect_mean_1000_c]
    connect_standard_deviations = [standard_deviation_connect, standard_deviation_connect_10_c,
                                   standard_deviation_connect_100_c, standard_deviation_connect_1000_c]

    #print ("connect_means")
    #print (connect_means)
    #print ("connect_standard_deviations")
    #print (connect_standard_deviations)

    ac_means = [ac_mean, ac_mean_10_c, ac_mean_100_c, ac_mean_1000_c]
    ac_standard_deviations = [standard_deviation_ac, standard_deviation_ac_10_c,
                              standard_deviation_ac_100_c, standard_deviation_ac_1000_c]
    print ("ac_means")
    print (ac_means)
    print ("ac_standard_deviations")
    print (ac_standard_deviations)
    width = 0.4  # the width# of the bars: can also be len(x) sequence

    plt.rcParams["font.size"] = "14"
    fig, ax = plt.subplots(figsize=[8, 5])
    cmap = plt.cm.get_cmap('tab20c', 10)

    ax.bar(labels, startup_means, width, yerr=startup_standard_deviations, label='Startup Phase', hatch='', color=cmap.colors[0])

    ax.bar(labels, connect_means, width, yerr=connect_standard_deviations, bottom=startup_means,
           label='Connecting Phase', hatch='', color=cmap.colors[1])

    ax.bar(labels, ac_means, width, yerr=ac_standard_deviations, bottom= [sum(i) for i in zip(startup_means, connect_means)]  ,
           label='Access Control Phase', color=cmap.colors[2])

    ax.set_ylabel('Time (s)')
    #ax.set_title('Implementation performance depending on Access Control Policies')
    ax.legend()
    plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.7)

    plt.savefig('figures/plot1.png', dpi=300)
    plt.show()
elif "plot2" in arg_list:

    labels = ['1 Credential', '10 Credentials', '100 Credentials']
    startup_means = [startup_mean, startup_mean_10_c, startup_mean_100_c]
    startup_standard_deviations = [standard_deviation_startup, standard_deviation_startup_10_c,
                                   standard_deviation_startup_100_c]

    connect_means = [connect_mean, connect_mean_10_c, connect_mean_100_c]
    connect_standard_deviations = [standard_deviation_connect, standard_deviation_connect_10_c,
                                   standard_deviation_connect_100_c]
    ac_means = [ac_mean, ac_mean_10_c, ac_mean_100_c]
    ac_standard_deviations = [standard_deviation_ac, standard_deviation_ac_10_c,
                              standard_deviation_ac_100_c]

    # labels = ['π₁', 'π₂', 'π₃']
    # labels = ["π₁"]
    # startup_means = [17, 28, 32]
    # standard_deviation_startup = [2, 3, 4]
    # conn_phase_mean = [17, 28, 32]
    # conn_phase_std = [2, 3, 4]

    # ac_phase_mean = [25, 32, 34]
    # ac_phase_std = [3, 5, 2]

    width = 0.25  # the width# of the bars: can also be len(x) sequence

    fig, ax = plt.subplots()

    ax.bar(labels, startup_means, width, yerr=startup_standard_deviations, label='Startup Phase', hatch='')

    ax.bar(labels, connect_means, width, yerr=connect_standard_deviations, bottom=startup_means,
           label='Connecting Phase', hatch='')

    ax.bar(labels, ac_means, width, yerr=ac_standard_deviations, bottom= [sum(i) for i in zip(startup_means, connect_means)]  ,
           label='Access Control Phase')

    ax.set_ylabel('Time (s)')
    #ax.set_title('Implementation performance depending on Access Control Policies')
    ax.legend()
    plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.7)
    plt.savefig('figures/plot2.png', dpi=300)

    plt.show()

#each subphase
if "plot3" in arg_list:
    #show duration breakdown of different phases
    print(register_did_10_c)
    # STARTUP
    #register_did_10_c
    rd = durations_10_credential.get_register_did_startup_phase_duration()
    #init_agents_10_c
    ia = durations_10_credential.get_init_agents_startup_phase_duration()
    #publish_schema_10_c
    ps = durations_10_credential.get_publish_schema_startup_phase_duration()

    # Connect
    #conn_alice_tecnico_10_c
    cat = durations_10_credential.get_conn_alice_tecnico_connect_phase_duration()
    #emit_credential_10_c
    emit = durations_10_credential.get_emit_credential_connect_phase_duration()
    #conn_alice_qualichain_10_c
    caq = durations_10_credential.get_conn_alice_qualichain_connect_phase_duration()
    #avg_time_per_cred_10_c

    # Access Control
    #construct_proof_request_to_alice
    cpra = durations_10_credential.get_construct_proof_request_to_alice_ac_phase_duration()
    #construct_proof_to_tecnico
    cpt = durations_10_credential.get_construct_proof_to_tecnico_ac_phase_duration()
    #handle_proof_from_alice
    hpa = durations_10_credential.get_handle_proof_from_alice_ac_phase_duration()
    #eval_access_control
    eac = durations_10_credential.get_eval_access_control_ac_phase_duration()

    print("Duracao emissao: ", emit)
    print("Total: ", cat + emit + caq + cpra + cpt + hpa + eac)
    #plt.rc('image', cmap='gray')
    width = 1.5 # the width# of the bars: can also be len(x) sequence
    label = ["Access Control Process Duration"]
    plt.rcParams["font.size"] = "14"
    fig, ax = plt.subplots(figsize=[8, 5])

    viridis = plt.cm.get_cmap('tab20c', 10)
    #viridis.colors = viridis.colors[::-1]

    ax.bar(label, cat, width, yerr=None,
           bottom=None,
           color=viridis.colors[0],
           label='Connect Alice-Tecnico')

    ax.bar(label, emit, width, yerr=None,
           bottom=cat,
           color=viridis.colors[1],
           label='Emit Credential to Alice')

    ax.bar(label, caq, width, yerr=None,
           bottom=cat + emit,
           color=viridis.colors[2],
           #hatch='/',
           label='Connect Alice-Qualichain')

    ax.bar(label, cpra, width, yerr=None,
           bottom=cat + emit + caq,
           color=viridis.colors[3],
           #hatch='X',
           label='Construct proof request to Alice')

    ax.bar(label, cpt, width, yerr=None,
           bottom=cat + emit + caq + cpra,
           color=viridis.colors[4],
           label='Construct proof to Tecnico')

    ax.bar(label, hpa, width, yerr=None,
           bottom=cat + emit + caq + cpra + cpt,
           color=viridis.colors[5],
           label='Handle proof from Alice')

    ax.bar(label, eac * 100, width, yerr=None,
           bottom=cat + emit + caq + cpra + cpt + hpa,
           color= viridis.colors[6],
           label='Evaluate Access Control Request')

    ax.set_ylabel('Time (s)')
    ax.set_xlim(-3, 8)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper right')
    # ax.set_title('Implementation performance depending on Access Control Policies')
    plt.grid(linestyle='--', linewidth=1, axis='y', alpha=0.7)
    plt.savefig('figures/plot3.png', dpi=300)
    plt.show()

if "plot4" in arg_list:
    print(register_did_10_c)
    # STARTUP
    #register_did_10_c
    rd = durations_10_credential.get_register_did_startup_phase_duration()
    #init_agents_10_c
    ia = durations_10_credential.get_init_agents_startup_phase_duration()
    #publish_schema_10_c
    ps = durations_10_credential.get_publish_schema_startup_phase_duration()

    # Connect
    #conn_alice_tecnico_10_c
    cat = durations_10_credential.get_conn_alice_tecnico_connect_phase_duration()
    #emit_credential_10_c
    emit = durations_10_credential.get_emit_credential_connect_phase_duration()
    #conn_alice_qualichain_10_c
    caq = durations_10_credential.get_conn_alice_qualichain_connect_phase_duration()
    #avg_time_per_cred_10_c

    # Access Control
    #construct_proof_request_to_alice
    cpra = durations_10_credential.get_construct_proof_request_to_alice_ac_phase_duration()
    #construct_proof_to_tecnico
    cpt = durations_10_credential.get_construct_proof_to_tecnico_ac_phase_duration()
    #handle_proof_from_alice
    hpa = durations_10_credential.get_handle_proof_from_alice_ac_phase_duration()
    #eval_access_control
    eac = durations_10_credential.get_eval_access_control_ac_phase_duration()


    width = 1  # the width# of the bars: can also be len(x) sequence
    label = ["Access Control Process Duration"]
    fig, ax = plt.subplots()

    ax.bar(label, rd, width, yerr=None, label='Register DIDs', hatch='')

    ax.bar(label, ia, width, yerr=None, bottom=rd,
           label='Initialize Agents', hatch='')

    ax.bar(label, ps, width, yerr=None,
           bottom=rd + ia,
           label='Publish Credential Schema')

    ax.bar(label, cat, width, yerr=None,
           bottom=rd + ia + ps,
           label='Connect Alice-Tecnico')

    ax.bar(label, emit, width, yerr=None,
           bottom=rd + ia + ps + cat,
           label='Emit Credential to Alice')

    ax.bar(label, caq, width, yerr=None,
           bottom=rd + ia + ps + cat + emit,
           label='Connect Alice-Qualichain')

    ax.bar(label, cpra, width, yerr=None,
           bottom=rd + ia + ps + cat + emit + caq,
           label='Construct proof request to Alice')

    ax.bar(label, cpt, width, yerr=None,
           bottom=rd + ia + ps + cat + emit + caq + cpra,
           label='Construct proof to Tecnico')

    ax.bar(label, hpa, width, yerr=None,
           bottom=rd + ia + ps + cat + emit + caq + cpra + cpt,
           label='Handle proof from Alice')

    ax.bar(label, eac, width, yerr=None,
           bottom=rd + ia + ps + cat + emit + caq + cpra + cpt + hpa,
           label='Evaluate Access Control Request')

    ax.set_ylabel('Time (s)')
    # ax.set_title('Implementation performance depending on Access Control Policies')
    ax.legend()
    plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.7)

    plt.show()