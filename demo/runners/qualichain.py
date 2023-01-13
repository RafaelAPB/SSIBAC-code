import asyncio
import json
import logging
import os
import sys
import base64
from urllib.parse import urlparse
import binascii
import logging
import time
import casbin
from auth.dataObject import Object, ObjectSSI
from auth.subject import Subject

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa


from runners.support.agent import DemoAgent, default_genesis_txns
from runners.support.utils import (
    log_json,
    log_msg,
    log_status,
    log_timer,
    log_timer2,
    prompt,
    prompt_loop,
    require_indy,
)
SELF_ATTESTED = os.getenv("SELF_ATTESTED")
LOGGER = logging.getLogger(__name__)


global theirDid
global ssiDecision

class QualichainAgent(DemoAgent):
    def __init__(self, http_port: int, admin_port: int, **kwargs):
        super().__init__(
            "Qualichain Agent",
            http_port,
            admin_port,
            prefix="Qualichain",
            extra_args=["--auto-accept-invites", "--auto-accept-requests"],
            seed=2,
            **kwargs,
        )

        self.connection_id = None
        self._connection_ready = asyncio.Future()
        self.cred_state = {}
        # TODO define a dict to hold credential attributes based on
        # the credential_definition_id
        self.cred_attrs = {}

    def evaluateAccessControlRequest (self, decision):
        with log_timer2("EVALUATION-AC| Evaluating Access Control Request:"):
            #log_msg("Subject " , theirDid, "entering ABAC System", color="yellow")
            path_conf = './auth/abacSSI.conf'
            e = casbin.Enforcer(path_conf)
            sub = Subject(theirDid)
            obj = ObjectSSI('data1', decision)
            act = 'read'

            #log_msg("Subject " , theirDid, "requesting access to ", act, "on obj", obj, color="yellow")

            if e.enforce(sub, obj, act):
                pass
                #log_msg("Access granted", color="green")

            else:
                pass
                #log_msg("Access denied", color="red")

    async def detect_connection(self):
        await self._connection_ready

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    async def handle_connections(self, message):
        if message["connection_id"] == self.connection_id:
            if message["state"] == "active" and not self._connection_ready.done():
                self.log("Connected")
                self._connection_ready.set_result(True)

    async def handle_issue_credential(self, message):
        state = message["state"]
        credential_exchange_id = message["credential_exchange_id"]
        prev_state = self.cred_state.get(credential_exchange_id)
        if prev_state == state:
            return  # ignore
        self.cred_state[credential_exchange_id] = state

        self.log(
            "Credential: state =",
            state,
            ", credential_exchange_id =",
            credential_exchange_id,
        )

        if state == "request_received":
            log_msg("request_received", color="yellow")
            pass

    async def handle_present_proof(self, message):
        with log_timer2("EVALUATION-AC| Handling Presentation Proof from Alice:"):
            state = message["state"]

            presentation_exchange_id = message["presentation_exchange_id"]
            self.log(
                "Presentation: state =",
                state,
                ", presentation_exchange_id =",
                presentation_exchange_id,
            )

            if state == "presentation_received":
                #log_status("#27 Process the proof provided by X")
                #log_status("#28 Check if proof is valid")
                proof = await self.admin_POST(
                    f"/present-proof/records/{presentation_exchange_id}/"
                    "verify-presentation"
                )
                self.log("Proof =", proof["verified"])
                log_msg(proof)
                decision = proof["verified"]
                #log_msg("Proof presentation state updated = ", decision, color="yellow")
        self.evaluateAccessControlRequest(decision)

    async def handle_basicmessages(self, message):
        self.log("Received message:", message["content"])
        if message["content"] == "AC":
            log_msg("Event should be emmited")



async def input_invitation(agent):
    async for details in prompt_loop("Invite details: "):
        b64_invite = None
        try:
            url = urlparse(details)
            query = url.query
            if query and "c_i=" in query:
                pos = query.index("c_i=") + 4
                b64_invite = query[pos:]
            else:
                b64_invite = details
        except ValueError:
            b64_invite = details

        if b64_invite:
            try:
                padlen = 4 - len(b64_invite) % 4
                if padlen <= 2:
                    b64_invite += "=" * padlen
                invite_json = base64.urlsafe_b64decode(b64_invite)
                details = invite_json.decode("utf-8")
            except binascii.Error:
                pass
            except UnicodeDecodeError:
                pass

        if details:
            try:
                json.loads(details)
                break
            except json.JSONDecodeError as e:
                log_msg("Invalid invitation:", str(e))

    with log_timer2("Connect duration:"):
        connection = await agent.admin_POST("/connections/receive-invitation", details)
        agent.connection_id = connection["connection_id"]
        global theirDid
        theirDid = connection["my_did"]
        log_msg("DID of requester: ", theirDid, color="yellow")
        log_json(connection, label="Invitation response:")

        await agent.detect_connection()


async def main(start_port: int, show_timing: bool = False,    revocation: bool = False,):

    genesis = await default_genesis_txns()
    if not genesis:
        print("Error retrieving ledger genesis transactions")
        sys.exit(1)

    agent = None

    try:
        log_status("================= QUALICHAIN PEP/PDP =================0")
        log_status("#1 Provision an agent and wallet, get back configuration details")
        agent = QualichainAgent(
            start_port, start_port + 1, genesis_data=genesis, timing=show_timing
        )
        await agent.listen_webhooks(start_port + 2)
        await agent.register_did()

        with log_timer2("Startup duration:"):
            await agent.start_process()
        log_msg("Admin url is at:", agent.admin_url)
        log_msg("Endpoint url is at:", agent.endpoint)

        # Create a schema
        log_status("#3 Create a new schema on the ledger")
        with log_timer2("Publish schema duration:"):
            pass
            # TODO define schema
            # version = format(
            #     "%d.%d.%d"
            #     % (
            #         random.randint(1, 101),
            #         random.randint(1, 101),
            #         random.randint(1, 101),
            #     )
            # )
            # (
            #     schema_id,
            #     credential_definition_id,
            # ) = await agent.register_schema_and_creddef(
            #     "employee id schema",
            #     version,
            #     ["employee_id", "name", "date", "position"],
            # )



        log_msg("========== ACCEPTING CONNECTION FROM STUDENTS ====== ", color="red")
        await input_invitation(agent)

        async for option in prompt_loop(
            "(1) Issue Credential, (2) Send Proof Request, "
            + "(3) Send Message \n  (4) Evaluate Alice AC request \n (X) Exit? [1/2/3/X] "
        ):
            if option in "xX":
                break

            elif option == "1":
                log_status("#13 Issue credential offer to X")
                # TODO credential offers

            elif option == "2":
                pass

            elif option == "3":
                msg = await prompt("Enter message: ")
                await agent.admin_POST(
                    f"/connections/{agent.connection_id}/send-message", {"content": msg}
                )

            elif option == "4":
                    with log_timer2("EVALUATION-AC| Construct Proof Request:"):
                        log_status("#20 Request proof of degree from alice")
                        #, "restrictions": [{"issuer_did": agent.did}]
                        #, "restrictions": [{"issuer_did": agent.did}]
                        req_attrs = [
                            {"name": "name"},
                            {"name": "date"},
                        ]
                        if revocation:
                            req_attrs.append(
                                {
                                    "name": "degree",
                                    #"restrictions": [{"issuer_did": agent.did}],
                                    "non_revoked": {"to": int(time.time() - 1)},
                                },
                            )
                        else:
                            #, "restrictions": [{"issuer_did": agent.did}]
                            req_attrs.append(
                                {"name": "degree"}
                            )
                        if SELF_ATTESTED:
                            # test self-attested claims
                            req_attrs.append({"name": "self_attested_thing"}, )
                        req_preds = [
                            #TODO map to access control policies
                            # test zero-knowledge proofs
                            {
                                "name": "EQF",
                                "p_type": ">=",
                                "p_value": 5,
                                #"restrictions": [{"issuer_did": agent.did}],
                            }
                        ]

                        #
                        #req_preds = []
                        indy_proof_request = {
                            "name": "Proof of Education",
                            "version": "1.0",
                            "requested_attributes": {
                                f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
                            },
                            "requested_predicates": {
                                f"0_{req_pred['name']}_GE_uuid": req_pred
                                for req_pred in req_preds
                            },
                        }
                        if revocation:
                            indy_proof_request["non_revoked"] = {"to": int(time.time())}
                        proof_request_web_request = {
                            "connection_id": agent.connection_id,
                            "proof_request": indy_proof_request,
                        }
                        await agent.admin_POST(
                            "/present-proof/send-request", proof_request_web_request
                        )



        if show_timing:
            timing = await agent.fetch_timing()
            if timing:
                for line in agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = True
        try:
            if agent:
                await agent.terminate()
        except Exception:
            LOGGER.exception("Error terminating agent:")
            terminated = False

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Runs an Qualichain demo agent.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8040,
        metavar=("<port>"),
        help="Choose the starting port number to listen on",
    )
    parser.add_argument(
        "--timing", action="store_true", help="Enable timing information"
    )
    args = parser.parse_args()

    require_indy()

    try:
        asyncio.get_event_loop().run_until_complete(main(args.port, args.timing))
    except KeyboardInterrupt:
        os._exit(1)
