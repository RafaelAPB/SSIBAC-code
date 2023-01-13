import statistics


class EvaluationHelper:
    def __init__(self,experiment_number, total_runtime, register_did, avg_time_per_cred, init_agents,publish_schema,conn_alice_tecnico,emit_credential,conn_alice_qualichain,construct_proof_request_to_alice,construct_proof_to_tecnico,handle_proof_from_alice,eval_access_control):
        self.dimensions = experiment_number

        #Durations
        #Startup Phase
        self.register_did = register_did
        self.init_agents = init_agents
        self.publish_schema = publish_schema

        #Connecting Phase
        self.conn_alice_tecnico = conn_alice_tecnico
        self.emit_credential = emit_credential
        self.conn_alice_qualichain = conn_alice_qualichain

        #Access Control Phase
        self.construct_proof_request_to_alice = construct_proof_request_to_alice
        self.construct_proof_to_tecnico = construct_proof_to_tecnico
        self.handle_proof_from_alice = handle_proof_from_alice
        self.eval_access_control = eval_access_control


        #Helpers
        self.avg_time_per_cred = avg_time_per_cred
        self.total_runtime = total_runtime
        self.startup_phase_duration = 0
        self.connect_phase_duration = 0
        self.access_control_phase_duration = 0

    def print_all(self):
        print("Total Runtime: ", self.total_runtime)
        print("Register DIDs: ", self.register_did)
        print("Init Agents: ", self.init_agents)
        print("Publish Schema Duration: ", self.publish_schema)
        print("Connect Alice-IST: ", self.conn_alice_tecnico)
        print("Emit Credential: ", self.emit_credential)
        print("Average time per credential:", self.avg_time_per_cred)
        print("Connect Alice-Qualichain: ", self.conn_alice_qualichain)
        print("Construct Proof Request", self.handle_proof_from_alice)
        print("Construct proof to Tecnico", self.construct_proof_to_tecnico)
        print("Handling Presentation Proof", self.construct_proof_request_to_alice)
        print("Evaluating Access Control Request ", self.eval_access_control)

    def normalize(self):
        print("NORMALIZE")
        if len(self.eval_access_control) != self.dimensions:
            difference = self.dimensions - len(self.eval_access_control)
            for i in range(0, difference):
                self.eval_access_control = self.eval_access_control.append(self.eval_access_control)



    def get_dimensions(self):
        return self.dimensions

    ############################################### STARTUP PHASE #########
    def get_startup_phase_duration(self):
        return [self.register_did[i] + self.init_agents[i] + self.publish_schema[i] for i in range(self.get_dimensions())]

    def get_mean_startup_phase_duration(self):
        return statistics.mean(self.get_startup_phase_duration())

    def get_std_dev_startup_phase_duration(self):
        return statistics.stdev(self.get_startup_phase_duration())

    def get_register_did_startup_phase_duration(self):
        return statistics.mean(self.register_did)

    def get_init_agents_startup_phase_duration(self):
        return statistics.mean(self.init_agents)

    def get_publish_schema_startup_phase_duration(self):
        return statistics.mean(self.publish_schema)

    ############################# END OF STARTUP PHASE

    ############################################### CONNECT PHASE #########

    def get_connect_phase_duration(self):
        return [self.conn_alice_tecnico[i] + self.emit_credential[i] + self.conn_alice_qualichain[i] for i in range(self.get_dimensions())]

    def get_mean_connect_phase_duration(self):
        return statistics.mean(self.get_connect_phase_duration())

    def get_std_dev_connect_phase_duration(self):
        return statistics.stdev(self.get_connect_phase_duration())

    def get_conn_alice_tecnico_connect_phase_duration(self):
        return statistics.mean(self.conn_alice_tecnico)

    def get_emit_credential_connect_phase_duration(self):
        return statistics.mean(self.emit_credential)

    def get_conn_alice_qualichain_connect_phase_duration(self):
        return statistics.mean(self.conn_alice_qualichain)

    ############################# END OF CONNECT PHASE

    ############################################### ACCESS CONTROL PHASE #########

    def get_ac_phase_duration(self):
        return [self.construct_proof_request_to_alice[i] + self.construct_proof_to_tecnico[i] + self.handle_proof_from_alice[i] + self.eval_access_control[i] for i in range(0,1)]

    def get_mean_ac_phase_duration(self):
        return statistics.mean(self.get_ac_phase_duration())

    def get_std_dev_ac_phase_duration(self):
        return statistics.stdev(self.get_ac_phase_duration())

    def get_construct_proof_request_to_alice_ac_phase_duration(self):
        return statistics.mean(self.construct_proof_request_to_alice)

    def get_construct_proof_to_tecnico_ac_phase_duration(self):
        return statistics.mean(self.construct_proof_to_tecnico)

    def get_handle_proof_from_alice_ac_phase_duration(self):
        return statistics.mean(self.handle_proof_from_alice)

    def get_eval_access_control_ac_phase_duration(self):
        return statistics.mean(self.eval_access_control)

    ############################# END OF ACCESS CONTROL PHASE

    def get_total_time(self):
        return [self.get_startup_phase_duration()[i] + self.get_connect_phase_duration()[i] + self.get_ac_phase_duration()[i] for i in range(self.get_dimensions())]

    def get_total_time_mean(self):
        return statistics.mean(self.get_total_time())

    def get_total_time_standard_deviation(self):
        return statistics.stdev(self.get_total_time())
