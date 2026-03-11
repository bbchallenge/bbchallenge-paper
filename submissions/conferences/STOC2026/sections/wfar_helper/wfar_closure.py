from wfar_cert import WFARCert, WFARConfig


def main():
    # Example usage
    with open("wfar_cert.txt", "r") as f:
        cert_str = f.read().strip()

    cert = WFARCert.from_string(cert_str)
    print("Turing Machine:", cert.tm)
    print("Left WA states:", cert.left_wa.states)
    print("Right WA states:", cert.right_wa.states)
    print("Left special sets (>=0, <=0):", cert.left_special_sets)
    print("Right special sets (>=0, <=0):", cert.right_special_sets)
    print("\nAccepted configurations:")
    for config in sorted(
        cert.accepted_configs,
        key=lambda c: (c.tm_state, c.tm_read, c.left_wa_state, c.right_wa_state),
    ):
        print(config.format())

    # Generate visualizations
    cert.visualize()

    print("Checking forward closure...")

    check_forward_closure_set = set()
    initial_config = WFARConfig()
    to_add = [initial_config]

    check_impossible_configs = set()

    while to_add:
        config = to_add.pop()
        print(f"Checking {config.format()}")
        for next_config in cert.get_next_configs(config):
            print(f"  Child {next_config.format()}")
            matching_config = cert.find_matching_config(next_config)
            if matching_config is None:
                check_impossible_configs.add(next_config)
                continue
                # raise ValueError(f"No matching config found for {next_config.format()}")

            if matching_config in check_forward_closure_set:
                continue

            check_forward_closure_set.add(matching_config)
            to_add.append(matching_config)
            print("    Adding matching ", matching_config.format())

    print("Checking impossible configurations...")
    for config in check_impossible_configs:
        print(f"Checking {config.format()}")
        for next_config in cert.get_next_configs(config):
            print(f"  Child {next_config.format()}")
            for next_next_config in cert.get_next_configs(next_config):
                print(f"    Child {next_next_config.format()}")
                for next_next_next_config in cert.get_next_configs(next_next_config):
                    print(f"      Child {next_next_next_config.format()}")


if __name__ == "__main__":
    main()
