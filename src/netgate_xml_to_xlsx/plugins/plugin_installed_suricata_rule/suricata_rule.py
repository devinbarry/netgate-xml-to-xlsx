"""Suricata Rule plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from base64 import b64decode
from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "interface,descr,enable,alertsystemlog,alertsystemlog_facility,"
    "alertsystemlog_priority,append_http_log,append_stats_log,asn1_max_frames,autoflowbitrules,"
    "autofp_scheduler,block_drops_only,blockoffenders,blockoffendersip,blockoffenderskill,"
    "dcerpc_parser,delayed_detect,detect_eng_profile,dhcp_parser,dns_global_memcap,"
    "dns_parser_tcp,dns_parser_tcp_ports,dns_parser_udp,dns_parser_udp_ports,dns_request_flood_limit,"  # NOQA
    "dns_state_memcap,enable_async_sessions,enable_eve_log,enable_file_store,enable_http_log,"
    "enable_iprep,enable_midstream_sessions,enable_pcap_log,enable_stats_collection,enable_stats_log,"  # NOQA
    "enable_telegraf_stats,enable_tls_log,enable_tls_store,enable_verbose_logging,eve_log_alerts,"
    "eve_log_alerts_http,eve_log_alerts_metadata,"
    "eve_log_alerts_packet,eve_log_alerts_payload,eve_log_alerts_xff,eve_log_alerts_xff_deployment,eve_log_alerts_xff_header,"  # NOQA
    "eve_log_alerts_xff_mode,eve_log_anomaly,eve_log_anomaly_packethdr,eve_log_anomaly_type_applayer,"  # NOQA
    "eve_log_anomaly_type_decode,eve_log_anomaly_type_stream,"
    "eve_log_dhcp,eve_log_dhcp_extended,eve_log_dns,eve_log_drop,"
    "eve_log_files,eve_log_files_hash,eve_log_files_magic,eve_log_flow,eve_log_ftp,"
    "eve_log_http,eve_log_http_extended,eve_log_http_extended_headers,eve_log_http2,eve_log_ikev2,"
    "eve_log_krb5,eve_log_mqtt,eve_log_netflow,eve_log_nfs,eve_log_rdp,eve_log_rfb,eve_log_sip,eve_log_smb,"  # NOQA
    "eve_log_smtp,eve_log_smtp_extended,eve_log_smtp_extended_fields,eve_log_snmp,eve_log_ssh,eve_log_stats,"  # NOQA
    "eve_log_stats_deltas,eve_log_stats_threads,eve_log_stats_totals,eve_log_tftp,eve_log_tls,"
    "eve_log_tls_extended_fields,"
    "eve_log_tls_extended,eve_output_type,eve_redis_key,eve_redis_mode,eve_redis_port,"
    "eve_redis_server,eve_systemlog_facility,eve_systemlog_priority,externallistname,"
    "file_store_logdir,flow_emerg_recovery,"
    "flow_hash_size,flow_icmp_emerg_established_timeout,flow_icmp_emerg_new_timeout,flow_icmp_established_timeout,flow_icmp_new_timeout,"  # NOQA
    "flow_memcap,flow_prealloc,flow_prune,flow_tcp_closed_timeout,flow_tcp_emerg_closed_timeout,"
    "flow_tcp_emerg_established_timeout,flow_tcp_emerg_new_timeout,flow_tcp_established_timeout,flow_tcp_new_timeout,flow_udp_emerg_established_timeout,"  # NOQA
    "flow_udp_emerg_new_timeout,flow_udp_established_timeout,flow_udp_new_timeout,frag_hash_size,frag_memcap,"  # NOQA
    "ftp_parser,homelistname,host_hash_size,host_memcap,host_os_policy,"
    "host_os_policy,host_prealloc,http_log_extended,http_parser,http_parser_memcap,"
    "http2_parser,ikev2_parser,imap_parser,inspect_recursion_limit,intf_promisc_mode,"
    "intf_snaplen,ip_frag_timeout,ip_max_frags,ip_max_trackers,ips_mode,"
    "ips_netmap_threads,ips_policy_enable,krb5_parser,libhtp_policy,max_pcap_log_files,"
    "max_pcap_log_size,max_pending_packets,max_synack_queued,mpm_algo,msn_parser,"
    "nfs_parser,ntp_parser,passlistname,rdp_parser,reassembly_depth,"
    "reassembly_memcap,reassembly_to_client_chunk,reassembly_to_server_chunk,rfb_parser,rule_sid_off,"  # NOQA
    "rulesets,runmode,sgh_mpm_context,sip_parser,smb_parser,"
    "smtp_parser,smtp_parser_compute_body_md5,smtp_parser_decode_base64,smtp_parser_decode_mime,smtp_parser_decode_quoted_printable,"  # NOQA
    "smtp_parser_extract_urls,snmp_parser,ssh_parser,stats_upd_interval,stream_bypass,stream_drop_invalid,stream_memcap,"  # NOQA
    "stream_prealloc_sessions,suppresslistname,tftp_parser,tls_detect_ports,tls_encrypt_handling,"  # NOQA
    "tls_ja3_fingerprint,tls_log_extended,tls_parser,uuid"
)


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Suricata Rules",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
        )

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""
        assert node is not None

        match node.tag:
            case "enable":
                # Override base.
                return str(node.text) if node.text is not None else ""

            case "eve_log_http_extended_headers" | "eve_log_smtp_extended_fields":
                els = [x.strip() for x in node.text.split(",")]
                els.sort(key=str.casefold)
                return "\n".join(els)

            case "file_store_logdir":
                return b64decode(node.text).decode("utf-8")

            case "host_os_policy" | "libhtp_policy":
                if node.tag == "host_os_policy":
                    node_names = "name,bind_to,policy".split(",")
                else:
                    node_names = (
                        "name,bind_to,personality,request-body-limit,response-body-limit,"
                        "double-decode-path,double-decode-query,uri-include-all"
                    ).split(",")
                cell = []
                item_nodes = xml_findall(node, "item")
                for item_node in item_nodes:
                    cell.append(self.load_cell(item_node, node_names))
                    cell.append("")
                if len(cell) > 0 and cell[-1] == "":
                    cell = cell[:-1]
                return "\n".join(cell)

            case "rule_sid_off" | "rulesets":
                els = [x.strip() for x in node.text.split("||")]
                els.sort(key=str.casefold)
                return "\n".join(els)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        suricata_node = xml_findone(parsed_xml, "installedpackages,suricata")
        if suricata_node is None:
            return
        self.report_unknown_node_elements(
            suricata_node, "config,passlist,rule,sid_mgmt_lists".split(",")
        )

        nodes = xml_findall(suricata_node, "rule")

        for node in nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))

            rows.append(self.sanity_check_node_row(node, row))

        rows.sort(key=lambda x: " ".join(x[0:1]).casefold())

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
        )
