#!/usr/bin/python3
"""Toggle a fixed allowlist of connection-event callsites; never reset hardware."""
import argparse
import json
import re
from pathlib import Path
SELECTORS = {'xone_dongle': ['xone_dongle_handle_loss', 'xone_dongle_add_client', 'xone_dongle_remove_client', 'xone_dongle_pair_client', 'xone_dongle_enable_client_encryption', 'xone_dongle_pairing_handler', 'xone_dongle_fw_requester', 'xone_dongle_fw_load', 'xone_mt76_load_firmware', 'xone_mt76_send_firmware', 'xone_mt76_init_radio', 'xone_mt76_suspend_radio', 'xone_mt76_resume_radio', 'xone_dongle_disconnect', 'xone_dongle_suspend', 'xone_dongle_resume'], 'xone_gip': ['gip_handle_pkt_status', 'gip_handle_pkt_announce', 'gip_create_adapter', 'gip_destroy_adapter', 'gip_register_client', 'gip_unregister_client', 'gip_get_client']}

def catalog(path):
    sites=[]
    for line in path.read_text().splitlines():
        match=re.search(r'\[([^]]+)\](\S+)\s+=([\w]+)',line)
        if match and match[1] in SELECTORS and match[2] in SELECTORS[match[1]]:
            sites.append({'module':match[1], 'function':match[2], 'enabled':'p' in match[3]})
    return sites

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['enable','disable','status'])
    args=parser.parse_args()
    control=next((p for p in (Path('/proc/dynamic_debug/control'),Path('/sys/kernel/debug/dynamic_debug/control')) if p.exists()),None)
    if control is None:raise SystemExit('Dynamic debug control unavailable; check kernel CONFIG_DYNAMIC_DEBUG')
    if args.action!='status':
        flags='+pmf' if args.action=='enable' else '-pmf'
        # Separate writes keep every query short and independently validated.
        with control.open('w') as stream:
            for module,funcs in SELECTORS.items():
                for func in funcs:
                    stream.write(f'module {module} func {func} {flags}\n')
                    stream.flush()
    sites=catalog(control)
    print(json.dumps({'selected_sites':len(sites),'enabled_sites':sum(s['enabled'] for s in sites),'callsites':sites},indent=2))
    if args.action=='enable' and (not sites or not all(s['enabled'] for s in sites)):
        raise SystemExit('Not all available selected callsites were enabled')
if __name__=='__main__':main()
