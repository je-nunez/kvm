#!/usr/bin/env python

"""Get stats of all domains in local system using libvirt."""

from __future__ import print_function
import sys
import libvirt
import psutil


def get_all_doms_stats(domain_list):
    """
       Get stats of all domains.
       Returns a dictionary, with the dict keys being the domain names.
    """
    domain_stats = dict()
    for domain in domain_list:
        dom_name = domain.name()
        _, maxmem, mem, _, accum_cpu_total = domain.info()
        stats = dict()
        stats["maxmem"] = maxmem
        stats["mem"] = mem
        stats["accum_cpu_total"] = accum_cpu_total

        domain_stats[dom_name] = stats

    return domain_stats


def is_load_acceptable():
    """
       Returns dictionary
    """

    acceptable_cpu_threshold = 90  # or dynamically at
    acceptable_mem_threshold = 90  # run-time

    # in this call we should use "interval=<N>" for a delay
    cpu_load_pctg = psutil.cpu_percent(percpu=False)
    mem_stats = psutil.virtual_memory()

    is_ok = ((cpu_load_pctg < acceptable_cpu_threshold) and
                (mem_stats.percent < acceptable_mem_threshold))
    ret = {
        "is_ok": is_ok,
        "cpu": cpu_load_pctg,
        "mem": mem_stats.percent
    }

    return ret


def migrate(local_dom, dest_host):
    """
       Migrate a domain to another system.
       Return 0 if everything ok.
    """
    dest_conn = libvirt.open(dest_host)
    if dest_conn is None:
        # should raise exception to be more flexible
        print('Failed to open connection to ' + dest_host, file=sys.stderr)
        return -1

    new_dom = local_dom.migrate(dest_conn, flags=libvirt.VIR_MIGRATE_LIVE,
                                migrate_disks=None, destination_xml=None,
                                bandwidth=0)
    if new_dom is None:
        print('Could not migrate to the destination', file=sys.stderr)
        return -2

    return 0   # O means OK (or either raise exceptions above for errors)


def main():
    """
       Main function.
    """

    # dummy call to avoid warning at:
    # https://psutil.readthedocs.io/en/latest/#psutil.cpu_percent
    # "Warning the first time this function [cpu_percent] is called with
    #  interval = 0.0 or None it will return a meaningless 0.0 value
    #  which you are supposed to ignore."
    psutil.cpu_percent(percpu=False)

    conn = libvirt.openReadOnly(None)
    if conn is None:
        sys.exit('Failed to open local connection')

    try:
        filter_flags = libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE
        active_local_doms = conn.listAllDomains(filter_flags)
        if not active_local_doms:
            print('No domains exist under those filter flags',
                  file=sys.stderr)
        else:
            dom_stats = get_all_doms_stats(active_local_doms)

            for dom_name in dom_stats:
                (maxmem, mem, accum_cpu_total) = (
                    dom_stats[dom_name]["maxmem"],
                    dom_stats[dom_name]["mem"],
                    dom_stats[dom_name]["accum_cpu_total"]
                )
                print(dom_name + ' max memory is ' + str(maxmem))
                print(dom_name + ' memory is ' + str(mem))
                print(dom_name + ' cpu time is ' + str(accum_cpu_total))

            state = is_load_acceptable()
            if not state["is_ok"]:
                sorted_by_stat = sorted(dom_stats.items(),
                                        key=lambda kv: kv[1],
                                        reverse=True)
                print(str(sorted_by_stat))
                # migrate(a_local_dom, to_a_less_busy_host)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
