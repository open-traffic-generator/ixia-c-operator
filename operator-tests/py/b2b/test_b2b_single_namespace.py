import utils
import pytest
import time
from deepdiff import DeepDiff

@pytest.mark.sanity
def test_b2b_single_namespace():
    """
    Deploy b2b kne topology,
    - namespace - 1: ixia-c
    Delete b2b kne topology,
    - namespace - 1: ixia-c
    Validate,
    - total pods count
    - overall pods status
    - total service count
    - individual pod status
    - individual service status
    - operator pod health
    - socket connection
    - meshnet topologies
    - ixiatgs
    """
    namespace1 = 'ixia-c'
    namespace1_config = 'b2b_ixia_c_namespace.txt'
    expected_svcs = {
        'service-https-otg-controller': [443],
        'service-gnmi-otg-controller': [50051],
        'service-grpc-otg-controller': [40051],
        'service-otg-port-eth1': [5555, 50071],
        'service-otg-port-eth2': [5555, 50071]
    }

    expected_pods = [
        'otg-controller',
        'otg-port-eth1',
        'otg-port-eth2'
    ]

    expected_topology = [
        {
            "metadata": {
                "name": "otg-port-eth1",
                "namespace": "ixia-c",
            },
            "spec": {
                "links": [
                    {
                        "local_intf": "eth1",
                        "local_ip": "",
                        "peer_intf": "eth2",
                        "peer_ip": "",
                        "peer_pod": "otg-port-eth2",
                        "uid": 0
                    }
                ]
            },
        },
        {
            "metadata": {
                "name": "otg-port-eth2",
                "namespace": "ixia-c",
            },
            "spec": {
                "links": [
                    {
                        "local_intf": "eth2",
                        "local_ip": "",
                        "peer_intf": "eth1",
                        "peer_ip": "",
                        "peer_pod": "otg-port-eth1",
                        "uid": 0
                    }
                ]
            },
        }
    ]

    expected_ixiatgs = [
        {
            "metadata": {
                "name": "otg",
                "namespace": "ixia-c",
            },
            "spec": {
                "api_endpoint_map": {
                    "gnmi": {
                        "in": 50051
                    },
                    "grpc": {
                        "in": 40051
                    },
                    "https": {
                        "in": 443
                    }
                },
                "desired_state": "DEPLOYED",
                "interfaces": [
                    {
                        "name": "eth1"
                    },
                    {
                        "name": "eth2"
                    }
                ],
                "release": "local-latest"
            },
            "status": {
                "api_endpoint": {
                    "pod_name": "otg-controller",
                    "service_names": [
                        "service-gnmi-otg-controller",
                        "service-grpc-otg-controller",
                        "service-https-otg-controller"
                    ]
                },
                "interfaces": [
                    {
                        "interface": "eth1",
                        "name": "eth1",
                        "pod_name": "otg-port-eth1"
                    },
                    {
                        "interface": "eth2",
                        "name": "eth2",
                        "pod_name": "otg-port-eth2"
                    }
                ],
                "state": "DEPLOYED"
            }
        }
    ]
    try:
        op_rscount = utils.get_operator_restart_count()
        print("[Namespace:{}]Deploying KNE topology".format(
            namespace1
        ))
        utils.create_kne_config(namespace1_config, namespace1)
        utils.ixia_c_pods_ok(namespace1, expected_pods)
        utils.ixia_c_services_ok(namespace1, list(expected_svcs.keys()))
        op_rscount = utils.ixia_c_operator_ok(op_rscount)

        actual_topologies = utils.get_topologies(namespace1)
        assert not DeepDiff(expected_topology, actual_topologies, ignore_order=True), "expected topologies mismatched!!!"

        actual_ixiatgs = utils.get_ixiatgs(namespace1)
        assert not DeepDiff(expected_ixiatgs, actual_ixiatgs, ignore_order=True), "expected ixiatgs mismatched!!!"

        svc_ingress_map = utils.get_ingress_mapping(namespace1, list(expected_svcs.keys()))
        utils.socket_alive(expected_svcs, svc_ingress_map)

        print("[Namespace:{}]Deleting KNE topology".format(
            namespace1
        ))
        utils.delete_kne_config(namespace1_config, namespace1)
        utils.ixia_c_pods_ok(namespace1, [])
        utils.ixia_c_services_ok(namespace1, [])
        op_rscount = utils.ixia_c_operator_ok(op_rscount)

    finally:
        utils.delete_kne_config(namespace1_config, namespace1)
        utils.ixia_c_pods_ok(namespace1, [])
        utils.ixia_c_services_ok(namespace1, [])

        utils.wait_for(
            lambda: utils.topology_deleted(namespace1),
            'topology deleted',
            timeout_seconds=30
        )
        utils.delete_namespace(namespace1)
