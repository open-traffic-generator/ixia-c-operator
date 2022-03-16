import utils


def test_b2b_double_namespace():
    """
    Deploy b2b kne topology,
    - namespace - 1: ixia-c
    - namespace - 2: ixia-c-alt
    Delete b2b kne topology,
    - namespace - 1: ixia-c
    - namespace - 2: ixia-c-alt
    Validate,
    - total pods count
    - overall pods status
    - total service count
    - individual pod status
    - individual service status
    - operator pod health
    """
    namespace1 = 'ixia-c'
    namespace1_config = 'b2b_ixia_c_namespace.txt'
    namespace2 = 'ixia-c-alt'
    namespace2_config = 'b2b_ixia_c_alt_namespace.txt'
    expected_svcs = [
        'service-http-otg-controller',
        'service-gnmi-otg-controller',
        'service-grpc-otg-controller',
        'service-otg-port-eth1',
        'service-otg-port-eth2'
    ]

    expected_pods = [
        'otg-controller',
        'otg-port-eth1',
        'otg-port-eth2'
    ]
    try:
        op_rscount = utils.get_operator_restart_count()
        print("[Namespace:{}]Deploying KNE topology".format(
            namespace1
        ))
        utils.create_kne_config(namespace1_config, namespace1)
        utils.ixia_c_pods_ok(namespace1, expected_pods)
        utils.ixia_c_services_ok(namespace1, expected_svcs)

        print("[Namespace:{}]Deploying KNE topology".format(
            namespace2
        ))
        utils.create_kne_config(namespace2_config, namespace2)
        utils.ixia_c_pods_ok(namespace2, expected_pods)
        utils.ixia_c_services_ok(namespace2, expected_svcs)

        op_rscount = utils.ixia_c_operator_ok(op_rscount)

        print("[Namespace:{}]Deleting KNE topology".format(
            namespace1
        ))
        utils.delete_kne_config(namespace1_config, namespace1)
        utils.ixia_c_pods_ok(namespace1, [])
        utils.ixia_c_services_ok(namespace1, [])

        print("[Namespace:{}]Deleting KNE topology".format(
            namespace2
        ))
        utils.delete_kne_config(namespace2_config, namespace2)
        utils.ixia_c_pods_ok(namespace2, [])
        utils.ixia_c_services_ok(namespace2, [])

        op_rscount = utils.ixia_c_operator_ok(op_rscount)

    finally:
        utils.delete_kne_config(namespace1_config, namespace1)
        utils.delete_kne_config(namespace2_config, namespace2)

        utils.ixia_c_services_ok(namespace1, [])
        utils.ixia_c_pods_ok(namespace1, [])

        utils.ixia_c_services_ok(namespace2, [])
        utils.ixia_c_pods_ok(namespace2, [])

        utils.wait_for(
            lambda: utils.topology_deleted(namespace1),
            'topology deleted',
            timeout_seconds=30
        )
        utils.wait_for(
            lambda: utils.topology_deleted(namespace2),
            'topology deleted',
            timeout_seconds=30
        )
