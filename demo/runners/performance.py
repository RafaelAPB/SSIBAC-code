import asyncio
import logging
import os
import random
import sys
import casbin
import json
from auth.dataObject import ObjectSSI
from auth.subject import Subject
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa

from runners.support.agent import DemoAgent, default_genesis_txns
from runners.support.utils import log_timer, log_timer2, progress, require_indy
print (os.environ["TEST_TYPE"])
LOGGER = logging.getLogger(__name__)
global aliceDid
alice_seed = "d_000000000000000000000000290329"
policy = "1"

class BaseAgent(DemoAgent):
    def __init__(
        self,
        ident: str,
        port: int,
        prefix: str = None,
        use_routing: bool = False,
        **kwargs,
    ):
        if prefix is None:
            prefix = ident
        super().__init__(ident, port, port + 1, prefix=prefix, **kwargs)
        self._connection_id = None
        self._connection_ready = None
        self.credential_state = {}
        self.credential_event = asyncio.Event()
        self.revocations = []
        self.ping_state = {}
        self.ping_event = asyncio.Event()
        self.sent_pings = set()

    @property
    def connection_id(self) -> str:
        return self._connection_id

    @connection_id.setter
    def connection_id(self, conn_id: str):
        self._connection_id = conn_id
        self._connection_ready = asyncio.Future()

    async def get_invite(self, accept: str = "auto"):
        result = await self.admin_POST(
            "/connections/create-invitation", params={"accept": accept}
        )
        self.connection_id = result["connection_id"]
        return result["invitation"]

    async def receive_invite(self, invite, accept: str = "auto"):
        result = await self.admin_POST(
            "/connections/receive-invitation", invite, params={"accept": accept}
        )
        self.connection_id = result["connection_id"]
        return self.connection_id

    async def accept_invite(self, conn_id: str):
        await self.admin_POST(f"/connections/{conn_id}/accept-invitation")

    async def establish_inbound(self, conn_id: str, router_conn_id: str):
        await self.admin_POST(
            f"/connections/{conn_id}/establish-inbound/{router_conn_id}"
        )

    async def detect_connection(self):
        if not self._connection_ready:
            raise Exception("No connection to await")
        await self._connection_ready

    async def handle_connections(self, payload):
        if payload["connection_id"] == self.connection_id:
            if payload["state"] == "active" and not self._connection_ready.done():
                self.log("Connected")
                self._connection_ready.set_result(True)

    async def handle_issue_credential(self, payload):
        cred_ex_id = payload["credential_exchange_id"]
        rev_reg_id = payload.get("revoc_reg_id")
        cred_rev_id = payload.get("revocation_id")

        self.credential_state[cred_ex_id] = payload["state"]
        if rev_reg_id and cred_rev_id:
            self.revocations.append((rev_reg_id, cred_rev_id))
        self.credential_event.set()

    async def handle_ping(self, payload):
        thread_id = payload["thread_id"]
        if thread_id in self.sent_pings or (
            payload["state"] == "received"
            and payload["comment"]
            and payload["comment"].startswith("test-ping")
        ):
            self.ping_state[thread_id] = payload["state"]
            self.ping_event.set()

    async def check_received_creds(self) -> (int, int):
        while True:
            self.credential_event.clear()
            pending = 0
            total = len(self.credential_state)
            for result in self.credential_state.values():
                if result != "credential_acked":
                    pending += 1
            if self.credential_event.is_set():
                continue
            return pending, total

    async def update_creds(self):
        await self.credential_event.wait()

    async def check_received_pings(self) -> (int, int):
        while True:
            self.ping_event.clear()
            result = {}
            for thread_id, state in self.ping_state.items():
                if not result.get(state):
                    result[state] = set()
                result[state].add(thread_id)
            if self.ping_event.is_set():
                continue
            return result

    async def update_pings(self):
        await self.ping_event.wait()

    async def send_ping(self, ident: str = None) -> str:
        resp = await self.admin_POST(
            f"/connections/{self.connection_id}/send-ping",
            {"comment": f"test-ping {ident}"},
        )
        self.sent_pings.add(resp["thread_id"])

    def check_task_exception(self, fut: asyncio.Task):
        if fut.done():
            try:
                exc = fut.exception()
            except asyncio.CancelledError as e:
                exc = e
            if exc:
                self.log(f"Task raised exception: {str(exc)}")


class QualichainAgent(BaseAgent):
    def __init__(self, port: int, **kwargs):
        super().__init__("Qualichain", port, **kwargs)
        self.schema_id = None
        self.credential_definition_id = None
        self.revocation_registry_id = None

    async def handle_present_proof(self, message):
        state = message["state"]

        presentation_exchange_id = message["presentation_exchange_id"]
        self.log(
            "Presentation: state =",
            state,
            ", presentation_exchange_id =",
            presentation_exchange_id,
        )

        if state == "presentation_received":
            self.log("#27 Process the proof provided by X")
            self.log("#28 Check if proof is valid")
            proof = await self.admin_POST(
                f"/present-proof/records/{presentation_exchange_id}/"
                "verify-presentation"
            )
            self.log("Proof =", proof["verified"])
            self.log(proof)
            decision = proof["verified"]
            self.log("Proof presentation state updated = ", decision, color="yellow")
            self.evaluateAccessControlRequest(decision)

    def evaluateAccessControlRequest (self, decision):
        self.log("Subject " , aliceDid, "entering ABAC System", color="yellow")
        path_conf = './auth/abacSSI.conf'
        e = casbin.Enforcer(path_conf)
        sub = Subject(aliceDid)
        obj = ObjectSSI('data1', decision)
        act = 'read'

        self.log("Subject " , aliceDid, "requesting access to ", act, "on obj", obj, color="yellow")

        if e.enforce(sub, obj, act):
            self.log("Access granted", color="green")

        else:
            self.log("Access denied", color="red")

    async def send_presentation_proof(self):
        self.log("send presentatoin proof")
        req_attrs = []

        req_preds = [
            # TODO map to access control policies
            # test zero-knowledge proofs
            {
                "name": "EQF",
                "p_type": ">=",
                "p_value": 5,
                # "restrictions": [{"issuer_did": agent.did}],
            }
        ]
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
        self.log(self.connection_id)
        proof_request_web_request = {
            "connection_id": self.connection_id,
            "proof_request": indy_proof_request,
        }
        await self.admin_POST(
            "/present-proof/send-request", proof_request_web_request
        )


class AliceAgent(BaseAgent):
    def __init__(self, port: int, **kwargs):
        super().__init__("Alice", port, seed=alice_seed, **kwargs)
        self.extra_args = [
            "--auto-respond-credential-offer",
            "--auto-store-credential",
            "--monitor-ping",
        ]
        self.timing_log = "logs/alice_perf.log"

    async def set_tag_policy(self, cred_def_id, taggables):
        req_body = {"taggables": taggables}
        await self.admin_POST(f"/wallet/tag-policy/{cred_def_id}", req_body)

    async def handle_present_proof(self, message):
        state = message["state"]
        presentation_exchange_id = message["presentation_exchange_id"]
        presentation_request = message["presentation_request"]

        self.log(
            "Presentation: state =",
            state,
            ", presentation_exchange_id =",
            presentation_exchange_id,
        )

        if state == "request_received":
            self.log(
                "#24 Query for credentials in the wallet that satisfy the proof request"
            )

            # include self-attested attributes (not included in credentials)
            credentials_by_reft = {}
            revealed = {}
            self_attested = {}
            predicates = {}

            # select credentials to provide for the proof
            credentials = await self.admin_GET(
                f"/present-proof/records/{presentation_exchange_id}/credentials"
            )
            if credentials:
                for row in sorted(credentials, key=lambda c: int(c["cred_info"]["attrs"]["timestamp"]), reverse=True):
                    for referent in row["presentation_referents"]:
                        if referent not in credentials_by_reft:
                            credentials_by_reft[referent] = row

            for referent in presentation_request["requested_attributes"]:
                if referent in credentials_by_reft:
                    revealed[referent] = {
                        "cred_id": credentials_by_reft[referent]["cred_info"][
                            "referent"
                        ],
                        "revealed": True,
                    }
                else:
                    self_attested[referent] = "my self-attested value"

            for referent in presentation_request["requested_predicates"]:
                if referent in credentials_by_reft:
                    predicates[referent] = {
                        "cred_id": credentials_by_reft[referent]["cred_info"][
                            "referent"
                        ],
                        "revealed": True,
                    }

            self.log("#25 Generate the proof")
            request = {
                "requested_predicates": predicates,
                "requested_attributes": revealed,
                "self_attested_attributes": self_attested,
            }

            self.log("#26 Send the proof to X")
            await self.admin_POST(
                (
                    "/present-proof/records/"
                    f"{presentation_exchange_id}/send-presentation"
                ),
                request,
            )

class FaberAgent(BaseAgent):
    def __init__(self, port: int, **kwargs):
        super().__init__("Faber", port, **kwargs)
        self.schema_id = None
        self.credential_definition_id = None
        self.revocation_registry_id = None

    async def publish_defs(self, support_revocation: bool = False):
        # create a schema
        self.log("Publishing test schema")
        version = format(
            "%d.%d.%d"
            % (random.randint(1, 101), random.randint(1, 101), random.randint(1, 101))
        )
        schema_body = {
            "schema_name": "degree schema",
            "schema_version": version,
            "attributes": ["firstName", "lastName", "age", "id", "timestamp", "university", "type", "name", "EQF",
                           "course", "grade", "gradeScale", "skills", "degreeId"],
        }
        schema_response = await self.admin_POST("/schemas", schema_body)
        self.schema_id = schema_response["schema_id"]
        self.log(f"Schema ID: {self.schema_id}")

        # create a cred def for the schema
        self.log("Publishing test credential definition")
        credential_definition_body = {
            "schema_id": self.schema_id,
            "support_revocation": support_revocation,
        }
        credential_definition_response = await self.admin_POST(
            "/credential-definitions", credential_definition_body
        )
        self.credential_definition_id = credential_definition_response[
            "credential_definition_id"
        ]
        self.log(f"Credential Definition ID: {self.credential_definition_id}")

        # create revocation registry
        if support_revocation:
            revoc_body = {
                "credential_definition_id": self.credential_definition_id,
            }
            revoc_response = await self.admin_POST(
                "/revocation/create-registry", revoc_body
            )
            self.revocation_registry_id = revoc_response["result"]["revoc_reg_id"]
            self.log(f"Revocation Registry ID: {self.revocation_registry_id}")

    async def send_credential(
        self, cred_attrs: dict, comment: str = None, auto_remove: bool = True
    ):
        cred_preview = {
            "attributes": [{"name": n, "value": v} for (n, v) in cred_attrs.items()]
        }
        await self.admin_POST(
            "/issue-credential/send",
            {
                "connection_id": self.connection_id,
                "cred_def_id": self.credential_definition_id,
                "credential_proposal": cred_preview,
                "comment": comment,
                "auto_remove": auto_remove,
                "revoc_reg_id": self.revocation_registry_id,
            },
        )

    async def revoke_credential(self, cred_ex_id: str):
        await self.admin_POST(
            f"/issue-credential/records/{cred_ex_id}/revoke?publish=true"
        )


class RoutingAgent(BaseAgent):
    def __init__(self, port: int, **kwargs):
        super().__init__("Router", port, **kwargs)


async def main(
    start_port: int,
    threads: int = 20,
    ping_only: bool = False,
    show_timing: bool = False,
    routing: bool = False,
    issue_count: int = 1,
    revoc: bool = False,
):
    if os.environ["TEST_TYPE"] == "TYPE_1":
        issue_count = 1
    elif os.environ["TEST_TYPE"] == "TYPE_2":
        issue_count = 10
    elif os.environ["TEST_TYPE"] == "TYPE_3":
        issue_count = 100
    elif os.environ["TEST_TYPE"] == "TYPE_4":
        issue_count = 1000

    print("TESTING| Issue Count Set to:", issue_count)

    #f = open("eval", "a")
    #f.write("===")
    genesis = await default_genesis_txns()
    if not genesis:
        print("Error retrieving ledger genesis transactions")
        sys.exit(1)

    alice = None
    faber = None
    qualichain = None
    aliceDid = None
    alice_router = None
    run_timer = log_timer2("EVALUATION| Total runtime:")
    run_timer.start()

    try:
        with log_timer2("EVALUATION|  Register DIDs:"):
            alice = AliceAgent(start_port, genesis_data=genesis, timing=show_timing)
            await alice.listen_webhooks(start_port + 2)
            aliceDid = await alice.register_did()

            faber = FaberAgent(start_port + 3, genesis_data=genesis, timing=show_timing)
            await faber.listen_webhooks(start_port + 5)
            await faber.register_did()

            qualichain = QualichainAgent(start_port + 6, genesis_data=genesis, timing=show_timing)
            await qualichain.listen_webhooks(start_port + 8)
            await qualichain.register_did()

            if routing:
                alice_router = RoutingAgent(
                    start_port + 6, genesis_data=genesis, timing=show_timing
                )
                await alice_router.listen_webhooks(start_port + 8)
                await alice_router.register_did()

        with log_timer2("EVALUATION| Initialize Agents:"):
            if alice_router:
                await alice_router.start_process()
            await alice.start_process()
            await faber.start_process()
            await qualichain.start_process()

        if not ping_only:
            with log_timer2("EVALUATION| Publish Schema:"):
                await faber.publish_defs(revoc)
                # await alice.set_tag_policy(faber.credential_definition_id, ["name"])

        with log_timer2("EVALUATION|  Connect Tecnico-Alice:"):
            if routing:
                router_invite = await alice_router.get_invite()
                alice_router_conn_id = await alice.receive_invite(router_invite)
                await asyncio.wait_for(alice.detect_connection(), 30)

            invite = await faber.get_invite()

            if routing:
                conn_id = await alice.receive_invite(invite, accept="manual")
                await alice.establish_inbound(conn_id, alice_router_conn_id)
                await alice.accept_invite(conn_id)
                await asyncio.wait_for(alice.detect_connection(), 30)
            else:
                await alice.receive_invite(invite)

            await asyncio.wait_for(faber.detect_connection(), 30)

        if show_timing:
            await alice.reset_timing()
            await faber.reset_timing()
            if routing:
                await alice_router.reset_timing()

        batch_size = 100

        semaphore = asyncio.Semaphore(threads)

        def done_send(fut: asyncio.Task):
            semaphore.release()
            faber.check_task_exception(fut)

        async def send_credential(index: int):
            await semaphore.acquire()
            comment = f"issue test credential {index}"
            attributes = {
                "firstName": "Alice",
                "lastName": "Smith",
                "age": "25",
                "id": "1234",
                "timestamp": str(int(time.time())),
                "university": "IST",
                "type": "BachelorDegree",
                "name": "Bachelor of Science",
                "EQF": "6",
                "course": "Computer Science",
                "grade": "4",
                "gradeScale": "0-4",
                "skills": "",
                "degreeId": "80970",
            }
            asyncio.ensure_future(
                faber.send_credential(attributes, comment, not revoc)
            ).add_done_callback(done_send)

        async def check_received_creds(agent, issue_count, pb):
            reported = 0
            iter_pb = iter(pb) if pb else None
            while True:
                pending, total = await agent.check_received_creds()
                complete = total - pending
                if reported == complete:
                    await asyncio.wait_for(agent.update_creds(), 30)
                    continue
                if iter_pb and complete > reported:
                    try:
                        while next(iter_pb) < complete:
                            pass
                    except StopIteration:
                        iter_pb = None
                reported = complete
                if reported == issue_count:
                    break

        async def send_ping(index: int):
            await semaphore.acquire()
            asyncio.ensure_future(faber.send_ping(str(index))).add_done_callback(
                done_send
            )

        async def check_received_pings(agent, issue_count, pb):
            reported = 0
            iter_pb = iter(pb) if pb else None
            while True:
                pings = await agent.check_received_pings()
                complete = sum(len(tids) for tids in pings.values())
                if complete == reported:
                    await asyncio.wait_for(agent.update_pings(), 30)
                    continue
                if iter_pb and complete > reported:
                    try:
                        while next(iter_pb) < complete:
                            pass
                    except StopIteration:
                        iter_pb = None
                reported = complete
                if reported >= issue_count:
                    break

        if ping_only:
            recv_timer = faber.log_timer(f"Completed {issue_count} ping exchanges in")
            batch_timer = faber.log_timer(f"Started {batch_size} ping exchanges in")
        else:
            recv_timer = faber.log_timer(
                f"EVALUATION| ({issue_count}) Emitted Credentials:"
            )
            batch_timer = faber.log_timer(
                f"Started {batch_size} credential exchanges in"
            )
        recv_timer.start()
        batch_timer.start()

        with progress() as pb:
            receive_task = None
            try:
                if ping_only:
                    issue_pg = pb(range(issue_count), label="Sending pings")
                    receive_pg = pb(range(issue_count), label="Responding pings")
                    check_received = check_received_pings
                    send = send_ping
                    completed = f"Done sending {issue_count} pings in"
                else:
                    issue_pg = pb(range(issue_count), label="Issuing credentials")
                    receive_pg = pb(range(issue_count), label="Receiving credentials")
                    check_received = check_received_creds
                    send = send_credential
                    completed = f"Done starting {issue_count} credential exchanges in"

                issue_task = asyncio.ensure_future(
                    check_received(faber, issue_count, issue_pg)
                )
                issue_task.add_done_callback(faber.check_task_exception)
                receive_task = asyncio.ensure_future(
                    check_received(alice, issue_count, receive_pg)
                )
                receive_task.add_done_callback(alice.check_task_exception)
                with faber.log_timer(completed):
                    for idx in range(0, issue_count):
                        await send(idx + 1)
                        if not (idx + 1) % batch_size and idx < issue_count - 1:
                            batch_timer.reset()

                await issue_task
                await receive_task
            except KeyboardInterrupt:
                if receive_task:
                    receive_task.cancel()
                print("Cancelled")

        recv_timer.stop()
        avg = recv_timer.duration / issue_count
        item_short = "ping" if ping_only else "cred"
        item_long = "ping exchange" if ping_only else "credential"
        #faber.log(f"EVALUATION| Average time per {item_long}: {avg:.4f}s ({1/avg:.4f}/s)")
        faber.log(f"EVALUATION| Average time per {item_long}: {avg:.4f}s")

        if alice.postgres:
            await alice.collect_postgres_stats(f"{issue_count} {item_short}s")
            for line in alice.format_postgres_stats():
                alice.log(line)
        if faber.postgres:
            await faber.collect_postgres_stats(f"{issue_count} {item_short}s")
            for line in faber.format_postgres_stats():
                faber.log(line)

        if revoc and faber.revocations:
            (rev_reg_id, cred_rev_id) = next(iter(faber.revocations))
            print(
                "Revoking and publishing cred rev id {cred_rev_id} "
                "from rev reg id {rev_reg_id}"
            )

        if show_timing:
            timing = await alice.fetch_timing()
            if timing:
                for line in alice.format_timing(timing):
                    alice.log(line)

            timing = await faber.fetch_timing()
            if timing:
                for line in faber.format_timing(timing):
                    faber.log(line)
            if routing:
                timing = await alice_router.fetch_timing()
                if timing:
                    for line in alice_router.format_timing(timing):
                        alice_router.log(line)
        #aquii
        # Test preesntation proof performance
        with log_timer2("EVALUATION|  Connect Alice-Qualichain:"):
            alice_invite = await alice.get_invite()
            await qualichain.receive_invite(alice_invite)
            await asyncio.wait_for(qualichain.detect_connection(), 30)
            # alice.reset_timing()
            # qualichain.reset_timing()
        #with log_timer2("E| Request presentation from Alice"):
            #await qualichain.send_presentation_proof()
            # time several issuings

    finally:
        terminated = True
        try:
            if alice:
                await alice.terminate()
        except Exception:
            LOGGER.exception("Error terminating agent:")
            terminated = False
        try:
            if faber:
                await faber.terminate()
        except Exception:
            LOGGER.exception("Error terminating agent:")
            terminated = False
        try:
            if qualichain:
                await qualichain.terminate()
        except Exception:
            LOGGER.exception("Error terminating agent:")
            terminated = False
        try:
            if alice_router:
                await alice_router.terminate()
        except Exception:
            LOGGER.exception("Error terminating agent:")
            terminated = False

    run_timer.stop()
    #message = ("Total runtime:",run_timer)
    #toWrite = str(message)
    #f.write(toWrite)
    #f.close()
    #toPrint = open("eval","r")
    #for line in toPrint:
    #    print (line, end = '')



    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Runs an automated credential issuance performance demo."
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        help="Set the number of credentials to issue",
    )
    parser.add_argument(
        "TYPE_1",
        default="",
        help="test type",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8030,
        metavar=("<port>"),
        help="Choose the starting port number to listen on",
    )
    parser.add_argument(
        "--ping",
        action="store_true",
        default=False,
        help="Only send ping messages between the agents",
    )
    parser.add_argument(
        "--routing", action="store_true", help="Enable inbound routing demonstration"
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=10,
        help="Set the number of concurrent exchanges to start",
    )
    parser.add_argument(
        "--timing", action="store_true", help="Enable detailed timing report"
    )
    args = parser.parse_args()

    require_indy()

    try:
        asyncio.get_event_loop().run_until_complete(
            main(
                args.port,
                args.threads,
                args.ping,
                args.timing,
                args.routing,
                args.count,
            )
        )
    except KeyboardInterrupt:
        os._exit(1)
